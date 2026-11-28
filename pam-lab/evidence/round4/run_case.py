"""Privileged access lab, round 4: measure one case under one setting on real open-source software.

Written AFTER guesses/guesses-round-4.md was merged (pull request #194),
sha256 0a7cac425ed7d3b6a265e56dc69880eb130e6ab72cd8cd95b7be3823b4cb2381.
Made-up data (Kaveri Finance). Runs on a GitHub Actions Ubuntu runner with Docker.

Usage:
    python3 pam-lab/evidence/round4/run_case.py --case 01 --setting off_a --out out/
Settings: none, all, off_a, off_b, off_c, joint (cases 01 and 04 only).
Writes out/r4-<case>-<setting>.json with the measured value, a step log and the software versions.
A setup failure is written as an error, never as a number: a harness bug must not look like a result.
"""
import argparse, base64, json, os, subprocess, sys, tempfile, time

KEYCLOAK = "quay.io/keycloak/keycloak:26.8.1"
OPENBAO = "docker.io/openbao/openbao:2.6.4"
POSTGRES = "docker.io/library/postgres:16-alpine"
DEBIAN = "docker.io/library/debian:bookworm-slim"
KIND_NODE = "kindest/node:v1.35.0@sha256:452d707d4862f52530247495d180205e029056831160e22870e37e3f6c1ac31f"
BUSYBOX = "docker.io/library/busybox:1.36.1"

SETTINGS = {"none": set(), "all": {"a", "b", "c"}, "off_a": {"b", "c"}, "off_b": {"a", "c"}, "off_c": {"a", "b"}}
JOINT = {"01": {"b"}, "04": {"c"}}  # the joint checks in the locked file: two controls off together

LOG = []
VERSIONS = {}


def log(msg):
    line = "%7.1fs %s" % (time.time() - T0, msg)
    LOG.append(line)
    print(line, flush=True)


def sh(cmd, check=True, input=None, timeout=600):
    r = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True, input=input, timeout=timeout)
    if check and r.returncode != 0:
        raise RuntimeError("command failed (%s): %s\n%s" % (r.returncode, cmd if isinstance(cmd, str) else " ".join(cmd), (r.stderr or r.stdout)[-1500:]))
    return r


def digest(image):
    r = sh(["docker", "image", "inspect", "--format", "{{index .RepoDigests 0}}", image], check=False)
    return r.stdout.strip() or image


def wait_until(fn, what, limit=240, step=3):
    end = time.time() + limit
    last = None
    while time.time() < end:
        try:
            if fn():
                return
        except Exception as e:  # keep trying until the limit
            last = e
        time.sleep(step)
    raise RuntimeError("timed out waiting for %s (%s)" % (what, last))


# ---------------------------------------------------------------- Keycloak helpers (cases 01 and 02)
def kc_start():
    import requests
    sh("docker rm -f kc", check=False)
    sh(["docker", "run", "-d", "--name", "kc", "-p", "8080:8080", "-e", "KC_BOOTSTRAP_ADMIN_USERNAME=admin",
        "-e", "KC_BOOTSTRAP_ADMIN_PASSWORD=admin", KEYCLOAK, "start-dev"])
    VERSIONS["keycloak"] = digest(KEYCLOAK)
    wait_until(lambda: requests.get("http://localhost:8080/realms/master", timeout=5).status_code == 200, "Keycloak", 300)
    log("Keycloak is up")


class KC:
    def __init__(self, realm):
        import requests
        self.r = requests
        self.base = "http://localhost:8080"
        self.realm = realm
        t = requests.post(self.base + "/realms/master/protocol/openid-connect/token",
                          data={"grant_type": "password", "client_id": "admin-cli", "username": "admin", "password": "admin"}, timeout=20)
        t.raise_for_status()
        self.h = {"Authorization": "Bearer " + t.json()["access_token"]}

    def adm(self, method, path, **kw):
        res = self.r.request(method, self.base + "/admin/realms" + path, headers=self.h, timeout=30, **kw)
        if res.status_code >= 300:
            raise RuntimeError("admin %s %s -> %s %s" % (method, path, res.status_code, res.text[:400]))
        return res

    def client(self, body):
        self.adm("POST", "/%s/clients" % self.realm, json=body)
        return self.adm("GET", "/%s/clients" % self.realm, params={"clientId": body["clientId"]}).json()[0]["id"]

    def user(self, name, password):
        self.adm("POST", "/%s/users" % self.realm, json={"username": name, "enabled": True, "emailVerified": True,
                 "firstName": name.title(), "lastName": "Lab", "email": name + "@kaveri.example", "requiredActions": [],
                 "credentials": [{"type": "password", "value": password, "temporary": False}]})
        return self.adm("GET", "/%s/users" % self.realm, params={"username": name, "exact": "true"}).json()[0]["id"]

    def token(self, client_id, secret, username, password, scope="openid"):
        res = self.r.post("%s/realms/%s/protocol/openid-connect/token" % (self.base, self.realm), timeout=20,
                          data={"grant_type": "password", "client_id": client_id, "client_secret": secret,
                                "username": username, "password": password, "scope": scope})
        if res.status_code != 200:
            raise RuntimeError("token request failed: %s %s" % (res.status_code, res.text[:400]))
        return res.json()["access_token"]


def jwt_local_claims(token, realm):
    """Check the signature and expiry against the realm's published keys, as an API that checks tokens on its own does."""
    import jwt
    jwk = jwt.PyJWKClient("http://localhost:8080/realms/%s/protocol/openid-connect/certs" % realm, cache_keys=False)
    key = jwk.get_signing_key_from_jwt(token).key
    return jwt.decode(token, key, algorithms=["RS256"], options={"verify_aud": False}, leeway=0)


def claims_unchecked(token):
    import jwt
    return jwt.decode(token, options={"verify_signature": False})


# ---------------------------------------------------------------- PA-R4-01
def case01(on):
    import requests
    kc_start()
    k = KC("master")
    life = 60 if "b" in on else 300
    k.adm("POST", "", json={"realm": "kaveri", "enabled": True, "accessTokenLifespan": life})
    k.realm = "kaveri"
    k.adm("POST", "/kaveri/roles", json={"name": "pam-admin"})
    role = k.adm("GET", "/kaveri/roles/pam-admin").json()
    k.client({"clientId": "pam-cli", "secret": "cli-secret", "publicClient": False, "directAccessGrantsEnabled": True,
              "standardFlowEnabled": False})
    k.client({"clientId": "pam-api", "secret": "api-secret", "publicClient": False, "directAccessGrantsEnabled": False,
              "standardFlowEnabled": False, "serviceAccountsEnabled": True})
    uid = k.user("asha", "Lab-pass-01!")
    k.adm("POST", "/kaveri/users/%s/role-mappings/realm" % uid, json=[role])
    tok = k.token("pam-cli", "cli-secret", "asha", "Lab-pass-01!")
    if "pam-admin" not in claims_unchecked(tok).get("realm_access", {}).get("roles", []):
        raise RuntimeError("setup: the token does not carry pam-admin")
    log("token issued with pam-admin, life %ss" % life)

    def api_accepts():
        if "a" in on:  # online check: ask Keycloak about the token on every call
            res = requests.post("http://localhost:8080/realms/kaveri/protocol/openid-connect/token/introspect", timeout=10,
                                data={"token": tok, "client_id": "pam-api", "client_secret": "api-secret"})
            body = res.json()
            return bool(body.get("active")) and "pam-admin" in body.get("realm_access", {}).get("roles", [])
        try:
            c = jwt_local_claims(tok, "kaveri")
        except Exception:
            return False
        return "pam-admin" in c.get("realm_access", {}).get("roles", [])

    if not api_accepts():
        raise RuntimeError("setup: the API refuses the token before the role is removed")
    k.adm("DELETE", "/kaveri/users/%s/role-mappings/realm" % uid, json=[role])
    if "c" in on:
        k.adm("POST", "/kaveri/users/%s/logout" % uid)
    t_removed = time.time()
    log("role removed%s" % (", sessions logged out" if "c" in on else ""))
    for t in range(0, 601, 15):
        while time.time() < t_removed + t:
            time.sleep(0.2)
        ok = api_accepts()
        log("t=%ss accepted=%s" % (t, ok))
        if not ok:
            return t
    return 600


# ---------------------------------------------------------------- PA-R4-02
def case02(on):
    kc_start()
    k = KC("master")
    k.adm("POST", "", json={"realm": "kaveri", "enabled": True})
    k.realm = "kaveri"
    k.adm("POST", "/kaveri/client-scopes", json={"name": "db-admin", "protocol": "openid-connect",
          "attributes": {"include.in.token.scope": "true", "display.on.consent.screen": "false"}})
    sid = [s for s in k.adm("GET", "/kaveri/client-scopes").json() if s["name"] == "db-admin"][0]["id"]
    parent = k.client({"clientId": "parent-agent", "secret": "parent-secret", "publicClient": False,
                       "directAccessGrantsEnabled": True, "standardFlowEnabled": False,
                       "protocolMappers": [
                           {"name": "aud-db-api", "protocol": "openid-connect", "protocolMapper": "oidc-audience-mapper",
                            "config": {"included.custom.audience": "db-api", "access.token.claim": "true"}},
                           {"name": "aud-sub-agent", "protocol": "openid-connect", "protocolMapper": "oidc-audience-mapper",
                            "config": {"included.custom.audience": "sub-agent", "access.token.claim": "true"}}]})
    k.adm("PUT", "/kaveri/clients/%s/default-client-scopes/%s" % (parent, sid))
    k.client({"clientId": "sub-agent", "secret": "sub-secret", "publicClient": False, "directAccessGrantsEnabled": False,
              "standardFlowEnabled": False, "attributes": {"standard.token.exchange.enabled": "true"}})
    k.user("agent-runner", "Lab-pass-02!")
    parent_tok = k.token("parent-agent", "parent-secret", "agent-runner", "Lab-pass-02!")
    pc = claims_unchecked(parent_tok)
    log("parent token aud=%s scope=%s" % (pc.get("aud"), pc.get("scope")))
    if "db-admin" not in pc.get("scope", "").split():
        raise RuntimeError("setup: the parent token lacks db-admin")

    def exchange():
        res = k.r.post("http://localhost:8080/realms/kaveri/protocol/openid-connect/token", timeout=20, data={
            "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange", "client_id": "sub-agent", "client_secret": "sub-secret",
            "subject_token": parent_tok, "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
            "requested_token_type": "urn:ietf:params:oauth:token-type:access_token"})
        if res.status_code != 200:
            raise RuntimeError("setup: token exchange failed: %s %s" % (res.status_code, res.text[:400]))
        return res.json()["access_token"]

    def admin_endpoint_accepts(tok):
        try:
            c = jwt_local_claims(tok, "kaveri")
        except Exception as e:
            log("signature or expiry check failed: %s" % e)
            return False
        aud = c.get("aud") or []
        aud = [aud] if isinstance(aud, str) else aud
        if "b" in on and "db-api" not in aud:
            return False
        if "c" in on and "db-admin" not in (c.get("scope") or "").split():
            return False
        return True

    reached = 0
    for i in range(1, 4):
        tok = exchange() if "a" in on else parent_tok
        c = claims_unchecked(tok)
        ok = admin_endpoint_accepts(tok)
        log("sub-agent %d: aud=%s scope=%s reached=%s" % (i, c.get("aud"), c.get("scope"), ok))
        reached += ok
    return reached


# ---------------------------------------------------------------- PA-R4-03
def case03(on):
    import requests
    for n in ("bao", "pg"):
        sh("docker rm -f %s" % n, check=False)
    sh("docker network rm lab", check=False)
    sh("docker network create lab")
    sh(["docker", "run", "-d", "--name", "pg", "--network", "lab", "-e", "POSTGRES_PASSWORD=pgroot", POSTGRES])
    sh(["docker", "run", "-d", "--name", "bao", "--network", "lab", "--cap-add", "IPC_LOCK", "-p", "8200:8200", OPENBAO,
        "server", "-dev", "-dev-root-token-id=root", "-dev-listen-address=0.0.0.0:8200"])
    VERSIONS["openbao"] = digest(OPENBAO)
    VERSIONS["postgres"] = digest(POSTGRES)
    H = {"X-Vault-Token": "root"}
    B = "http://localhost:8200/v1"
    wait_until(lambda: sh(["docker", "exec", "pg", "pg_isready", "-U", "postgres"], check=False).returncode == 0, "PostgreSQL")
    wait_until(lambda: requests.get(B + "/sys/health", timeout=5).status_code == 200, "OpenBao")
    log("OpenBao and PostgreSQL are up")

    def login(user, password):
        r = sh(["docker", "run", "--rm", "--network", "lab", POSTGRES, "psql",
                "postgresql://%s:%s@pg:5432/postgres?sslmode=disable" % (user, password), "-tAc", "select 1"], check=False, timeout=60)
        return r.returncode == 0 and r.stdout.strip() == "1"

    if "a" in on:
        def ok(res):
            if res.status_code >= 300:
                raise RuntimeError("OpenBao %s %s" % (res.status_code, res.text[:400]))
            return res
        ok(requests.post(B + "/sys/mounts/database", headers=H, json={"type": "database"}, timeout=20))
        ok(requests.post(B + "/database/config/pg", headers=H, timeout=60, json={
            "plugin_name": "postgresql-database-plugin", "allowed_roles": "*", "username": "postgres", "password": "pgroot",
            "connection_url": "postgresql://{{username}}:{{password}}@pg:5432/postgres?sslmode=disable"}))
        ttl = "5m" if "b" in on else "768h"
        ok(requests.post(B + "/database/roles/task", headers=H, timeout=20, json={
            "db_name": "pg", "default_ttl": ttl, "max_ttl": ttl,
            "creation_statements": ["CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}';"]}))
        cred = ok(requests.get(B + "/database/creds/task", headers=H, timeout=30)).json()
        user, pw, lease = cred["data"]["username"], cred["data"]["password"], cred["lease_id"]
        log("per-task credential issued, lease %s" % ttl)
    else:
        user, pw, lease = "svc_static", "Static-pass-03!", None
        sh(["docker", "exec", "pg", "psql", "-U", "postgres", "-c", "CREATE ROLE svc_static WITH LOGIN PASSWORD 'Static-pass-03!'"])
        log("stored password in use")
    if not login(user, pw):
        raise RuntimeError("setup: the credential does not work at the start of the task")
    time.sleep(120)  # the 2-minute task
    if "c" in on and lease:
        res = requests.put(B + "/sys/leases/revoke", headers=H, json={"lease_id": lease}, timeout=30)
        if res.status_code >= 300:
            raise RuntimeError("revoke failed %s %s" % (res.status_code, res.text[:300]))
        log("lease revoked at task end")
    t_end = time.time()
    for m in range(0, 31):
        while time.time() < t_end + 60 * m:
            time.sleep(0.5)
        works = login(user, pw)
        log("minute %d: login works=%s" % (m, works))
        if not works:
            return m
    return 30


# ---------------------------------------------------------------- PA-R4-04
DOCKERFILE_SSH = """FROM %s
RUN apt-get update && apt-get install -y --no-install-recommends openssh-server sudo && rm -rf /var/lib/apt/lists/* \\
 && mkdir -p /run/sshd && ssh-keygen -A \\
 && groupadd pamadmins && useradd -m -s /bin/bash -G pamadmins asha \\
 && echo '%%pamadmins ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/pamadmins && chmod 440 /etc/sudoers.d/pamadmins \\
 && mkdir -p /home/asha/.ssh && chmod 700 /home/asha/.ssh
COPY key.pub /home/asha/.ssh/authorized_keys
RUN chown -R asha:asha /home/asha/.ssh && chmod 600 /home/asha/.ssh/authorized_keys && passwd -d asha >/dev/null
CMD ["/usr/sbin/sshd", "-D", "-e"]
""" % DEBIAN


def case04(on):
    work = tempfile.mkdtemp()
    sh(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", os.path.join(work, "key")])
    open(os.path.join(work, "Dockerfile"), "w").write(DOCKERFILE_SSH)
    sh(["docker", "build", "-q", "-t", "pamlab-ssh", work], timeout=900)
    sh("docker rm -f sshlab", check=False)
    sh(["docker", "run", "-d", "--name", "sshlab", "-p", "2222:22", "pamlab-ssh"])
    VERSIONS["debian"] = digest(DEBIAN)
    VERSIONS["sudo"] = sh(["docker", "exec", "sshlab", "sudo", "-V"]).stdout.splitlines()[0]
    VERSIONS["openssh"] = (sh(["docker", "exec", "sshlab", "sshd", "-V"], check=False).stderr or "").strip().splitlines()[0:1]
    rules = []
    if "a" in on:
        rules.append("Defaults group_source=dynamic")
    if "c" in on:
        rules.append("Defaults logfile=/var/log/sudo-alert.log")
    if rules:
        sh(["docker", "exec", "-i", "sshlab", "sh", "-c", "cat > /etc/sudoers.d/controls && chmod 440 /etc/sudoers.d/controls && visudo -c"],
           input="\n".join(rules) + "\n")
    ssh = ["ssh", "-T", "-i", os.path.join(work, "key"), "-p", "2222", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null",
           "-o", "LogLevel=ERROR", "-o", "ServerAliveInterval=5", "asha@127.0.0.1", "bash"]
    wait_until(lambda: sh(ssh[:-1] + ["true"], check=False, timeout=20).returncode == 0, "sshd", 90)
    p = subprocess.Popen(ssh, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

    def run_sudo(i):
        if p.poll() is not None:
            return False
        try:
            p.stdin.write("sudo -n true </dev/null 2>/dev/null && echo SUDO_OK_%d || echo SUDO_NO_%d\n" % (i, i))
            p.stdin.flush()
        except (BrokenPipeError, OSError):
            return False
        end = time.time() + 20
        while time.time() < end:
            line = p.stdout.readline()
            if not line:
                return False
            if line.strip() == "SUDO_OK_%d" % i:
                return True
            if line.strip() == "SUDO_NO_%d" % i:
                return False
        return False

    if not run_sudo(0):
        raise RuntimeError("setup: sudo does not work in the session before removal")
    sh(["docker", "exec", "sshlab", "gpasswd", "-d", "asha", "pamadmins"])
    if "b" in on:
        sh(["docker", "exec", "sshlab", "pkill", "-KILL", "-u", "asha"], check=False)
    t0 = time.time()
    log("user removed from pamadmins%s" % (", sessions ended" if "b" in on else ""))
    ok = 0
    for i in range(1, 6):
        while time.time() < t0 + 30 * (i - 1):
            time.sleep(0.2)
        r = run_sudo(i)
        log("sudo %d at %ds: %s" % (i, 30 * (i - 1), "succeeded" if r else "refused or session gone"))
        ok += r
    if "c" in on:
        alerts = sh(["docker", "exec", "sshlab", "sh", "-c", "wc -l < /var/log/sudo-alert.log 2>/dev/null || echo 0"], check=False).stdout.strip()
        log("alert log lines: %s (an alert, it blocks nothing)" % alerts)
    try:
        p.kill()
    except Exception:
        pass
    return ok


# ---------------------------------------------------------------- PA-R4-05
def case05(on):
    import yaml
    work = tempfile.mkdtemp()
    sh("kind delete cluster --name pamlab", check=False)
    sh(["kind", "create", "cluster", "--name", "pamlab", "--image", KIND_NODE, "--wait", "180s"], timeout=900)
    VERSIONS["kind"] = sh(["kind", "version"]).stdout.strip()
    VERSIONS["kind_node"] = KIND_NODE
    admin_kc = os.path.join(work, "host.kubeconfig")
    open(admin_kc, "w").write(sh(["kind", "get", "kubeconfig", "--name", "pamlab"]).stdout)
    server = yaml.safe_load(open(admin_kc))["clusters"][0]["cluster"]["server"]
    K = ["kubectl", "--kubeconfig", admin_kc]
    VERSIONS["kubernetes"] = sh(K + ["version", "-o", "json"]).stdout.strip().replace("\n", " ")[:400]

    if "c" in on:  # audit log for exec into system namespaces: an alert, it blocks nothing
        policy = ("apiVersion: audit.k8s.io/v1\nkind: Policy\nrules:\n- level: Metadata\n  resources:\n  - group: \"\"\n"
                  "    resources: [\"pods/exec\"]\n  namespaces: [\"kube-system\", \"kube-public\", \"kube-node-lease\"]\n- level: None\n")
        node = "pamlab-control-plane"
        sh(["docker", "exec", "-i", node, "sh", "-c", "mkdir -p /etc/kubernetes/audit /var/log/kubernetes && cat > /etc/kubernetes/audit/policy.yaml"], input=policy)
        mf = os.path.join(work, "kube-apiserver.yaml")
        sh(["docker", "cp", node + ":/etc/kubernetes/manifests/kube-apiserver.yaml", mf])
        m = yaml.safe_load(open(mf))
        ctr = m["spec"]["containers"][0]
        ctr["command"] += ["--audit-policy-file=/etc/kubernetes/audit/policy.yaml", "--audit-log-path=/var/log/kubernetes/audit.log"]
        ctr.setdefault("volumeMounts", []).extend([{"name": "audit-policy", "mountPath": "/etc/kubernetes/audit", "readOnly": True},
                                                   {"name": "audit-log", "mountPath": "/var/log/kubernetes"}])
        m["spec"].setdefault("volumes", []).extend([{"name": "audit-policy", "hostPath": {"path": "/etc/kubernetes/audit", "type": "DirectoryOrCreate"}},
                                                    {"name": "audit-log", "hostPath": {"path": "/var/log/kubernetes", "type": "DirectoryOrCreate"}}])
        yaml.safe_dump(m, open(mf, "w"))
        sh(["docker", "cp", mf, node + ":/etc/kubernetes/manifests/kube-apiserver.yaml"])
        time.sleep(20)
        wait_until(lambda: sh(K + ["get", "--raw", "/readyz"], check=False, timeout=20).returncode == 0, "API server after audit change", 240)
        log("audit logging for exec into system namespaces is on")

    manifests = """
apiVersion: v1
kind: Namespace
metadata: {name: dev%s}
---
apiVersion: v1
kind: Namespace
metadata: {name: tools}
---
apiVersion: v1
kind: ServiceAccount
metadata: {name: developer, namespace: dev}
---
apiVersion: v1
kind: ServiceAccount
metadata: {name: ops-bot, namespace: tools}
---
apiVersion: v1
kind: Secret
metadata: {name: ops-bot-token, namespace: tools, annotations: {kubernetes.io/service-account.name: ops-bot}}
type: kubernetes.io/service-account-token
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata: {name: dev-pods, namespace: dev}
rules:
- {apiGroups: [""], resources: ["pods"], verbs: ["create", "get", "list", "watch", "delete"]}
- {apiGroups: [""], resources: ["pods/exec"], verbs: ["create", "get"]}
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata: {name: dev-pods, namespace: dev}
roleRef: {apiGroup: rbac.authorization.k8s.io, kind: Role, name: dev-pods}
subjects: [{kind: ServiceAccount, name: developer, namespace: dev}]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata: {name: read-secrets, namespace: tools}
rules: [{apiGroups: [""], resources: ["secrets"], verbs: ["get", "list"]}]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata: {name: read-secrets, namespace: tools}
roleRef: {apiGroup: rbac.authorization.k8s.io, kind: Role, name: read-secrets}
subjects: [{kind: ServiceAccount, name: developer, namespace: dev}]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata: {name: impersonate-engineer}
rules: [{apiGroups: [""], resources: ["users"], verbs: ["impersonate"], resourceNames: ["engineer"]}]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata: {name: developer-impersonates-engineer}
roleRef: {apiGroup: rbac.authorization.k8s.io, kind: ClusterRole, name: impersonate-engineer}
subjects: [{kind: ServiceAccount, name: developer, namespace: dev}]
""" % (", labels: {pod-security.kubernetes.io/enforce: restricted}" if "b" in on else "")
    if "a" not in on:
        manifests += """---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata: {name: engineer-standing-admin}
roleRef: {apiGroup: rbac.authorization.k8s.io, kind: ClusterRole, name: cluster-admin}
subjects: [{apiGroup: rbac.authorization.k8s.io, kind: User, name: engineer}]
"""
    manifests += """---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata: {name: ops-bot}
roleRef: {apiGroup: rbac.authorization.k8s.io, kind: ClusterRole, name: %s}
subjects: [{kind: ServiceAccount, name: ops-bot, namespace: tools}]
""" % ("view" if "b" in on else "cluster-admin")
    sh(K + ["apply", "-f", "-"], input=manifests)
    wait_until(lambda: sh(K + ["-n", "tools", "get", "secret", "ops-bot-token", "-o", "jsonpath={.data.token}"], check=False).stdout.strip() != "", "service account token")
    dev_token = sh(K + ["-n", "dev", "create", "token", "developer", "--duration=1h"]).stdout.strip()
    D = ["kubectl", "--kubeconfig", admin_kc, "--token", dev_token, "--user", "nobody"]  # the developer's credentials only
    sh(["kubectl", "--kubeconfig", admin_kc, "config", "set-credentials", "nobody"])

    def cluster_admin(extra):
        r = sh(extra + ["auth", "can-i", "*", "*", "--all-namespaces"], check=False, timeout=30)
        return r.stdout.strip() == "yes"

    if cluster_admin(D):
        raise RuntimeError("setup: the developer is already cluster-admin")
    paths = 0
    p1 = cluster_admin(D + ["--as", "engineer"])
    log("path 1, impersonate engineer: %s" % p1)
    paths += p1
    stolen = sh(D + ["-n", "tools", "get", "secret", "ops-bot-token", "-o", "jsonpath={.data.token}"], check=False).stdout.strip()
    p2 = bool(stolen) and cluster_admin(["kubectl", "--kubeconfig", admin_kc, "--user", "nobody", "--token", base64.b64decode(stolen).decode()])
    log("path 2, service account token read from tools: %s" % p2)
    paths += p2
    pod = {"apiVersion": "v1", "kind": "Pod", "metadata": {"name": "escape", "namespace": "dev"},
           "spec": {"containers": [{"name": "c", "image": BUSYBOX, "command": ["sleep", "3600"],
                                    "securityContext": {"privileged": True}, "volumeMounts": [{"name": "host", "mountPath": "/host"}]}],
                    "volumes": [{"name": "host", "hostPath": {"path": "/"}}]}}
    created = sh(D + ["create", "-f", "-"], input=json.dumps(pod), check=False)
    p3 = False
    if created.returncode == 0:
        sh(D + ["-n", "dev", "wait", "--for=condition=Ready", "pod/escape", "--timeout=180s"], timeout=240)
        conf = sh(D + ["-n", "dev", "exec", "escape", "--", "cat", "/host/etc/kubernetes/admin.conf"], check=False).stdout
        if conf:
            path = os.path.join(work, "stolen.conf")
            open(path, "w").write(conf)
            p3 = cluster_admin(["kubectl", "--kubeconfig", path, "--server", server])
    else:
        log("privileged pod refused: %s" % created.stderr.strip()[:200])
    log("path 3, privileged pod reads the node's admin.conf: %s" % p3)
    paths += p3
    return paths


CASES = {"01": case01, "02": case02, "03": case03, "04": case04, "05": case05}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", required=True, choices=sorted(CASES))
    ap.add_argument("--setting", required=True, choices=sorted(SETTINGS) + ["joint"])
    ap.add_argument("--out", default="out")
    a = ap.parse_args()
    if a.setting == "joint" and a.case not in JOINT:
        sys.exit("No joint check is stated for case %s." % a.case)
    on = JOINT[a.case] if a.setting == "joint" else SETTINGS[a.setting]
    T0 = time.time()
    result = {"id": "PA-R4-" + a.case, "setting": a.setting, "controls_on": sorted(on), "value": None, "error": None}
    try:
        result["value"] = CASES[a.case](on)
        log("measured value: %s" % result["value"])
    except Exception as e:
        result["error"] = str(e)[:2000]
        log("ERROR: %s" % result["error"])
    result["seconds"] = round(time.time() - T0, 1)
    result["versions"] = VERSIONS
    result["log"] = LOG
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "r4-%s-%s.json" % (a.case, a.setting)), "w") as f:
        json.dump(result, f, indent=1)
    sys.exit(1 if result["error"] else 0)
