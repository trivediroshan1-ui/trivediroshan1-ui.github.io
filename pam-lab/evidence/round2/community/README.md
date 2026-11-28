# Round 2 results from readers

Each file here is one reader's run of round 2 against their own model, added by pull request and merged by Roshan Trivedi. They are reader-submitted: the script records what it can about the model and the machine, but it can't prove nothing was changed.

## How to add yours

1. Start a model server. Any of these works: Ollama, LM Studio, llama.cpp's `llama-server`, or a hosted model with the common chat API.
2. From the top of the repository, run:

   ```
   python3 pam-lab/evidence/round2/round2.py --api ollama --endpoint http://localhost:11434 --model <name> --size small
   ```

   Use `--api openai --endpoint http://localhost:1234/v1` for LM Studio or another server with the common chat API. With llama.cpp's server, add `--no-think llamacpp` to switch thinking off. Size: `small` up to about 5 billion parameters, `medium` about 6 to 10 billion, `other` for anything else (reported, not scored).

   For a hosted model, put its key in the environment variable `R2_API_KEY`. The script never writes it to a file or prints it. Check that the provider's terms allow publishing results.

3. It takes a while: up to 1,530 answers on CPU. The script prints each answer as it goes.
4. It checks the locked files first, then writes `r2-<model>.json` and `r2-<model>.md` in `round2-out/`.
5. Open a pull request that adds only `r2-<model>.json` to this folder, unchanged. Say in the pull request what hardware you used.

Please don't include keys, real data or prompts from other work.
