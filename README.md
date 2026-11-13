RepoPilot
A local AI-powered bug-fixing prototype that tests its own patches, learns from failed attempts within a run, and escalates when it cannot find a passing fix.

RepoPilot explores a simple question: what happens when an AI code suggestion is treated as a hypothesis to test, rather than a fix to trust?

Given a Python source file and a corresponding unit test, RepoPilot reproduces the failure, asks a locally running coding model to propose a correction, runs the tests against that candidate, and uses the results to guide up to three attempts. If no candidate passes, it saves a structured report for human review.


The original source file is restored after candidate validation.
Design choices
- Validation before acceptance: Model output must pass executable tests; a convincing explanation or syntactically valid patch is not sufficient.
- Feedback-driven retries: Each new proposal receives the original code, the unit test, the baseline failure, and earlier attempts with their reports. This is in-context feedback, not model retraining.
- Separation of concerns: The orchestrator controls retries; the generator proposes changes; the validator runs tests; the checker detects structural duplicates; the escalation module writes review artifacts.
- Local inference: Ollama runs the coding model locally, avoiding per-call cloud API charges. Model performance depends on available hardware.
- Bounded retries and human handoff: After three unsuccessful proposals, RepoPilot saves evidence for review rather than looping indefinitely.
Quick start
Requirements: Python 3, Ollama, and a locally downloaded qwen2.5-coder:7b model.
1. Clone the repository and enter the project directory.
2. Create a virtual environment and install the Python dependencies:
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
3. Install Ollama and download the model:
   ollama pull qwen2.5-coder:7b
   Ensure Ollama is running before starting RepoPilot.
4. Run the included demo from the repository root:
   python main.py demo/cart.py --test-file demo/test_cart.py
The demo intentionally starts with a broken subtotal() implementation: two items totaling 400 cents produce 401 cents. A successful run detects the failing test, proposes a corrected implementation, validates it, and restores the original demo file. Your result may vary because patch generation uses a language model.

To inspect the demo test directly:
python -m unittest discover -s demo -p test_cart.py -v
This test is expected to fail against the original buggy demo source.
Project structure
File	Responsibility
main.py	CLI inputs, workflow orchestration, retry and escalation decisions
patch.py	Ollama prompt construction, structured patch generation, basic syntax validation
checks.py	AST-based comparison against unchanged or previously attempted code
validate.py	Subprocess-based Python unit-test execution and failure capture
escalate.py	JSON handoff report containing context and attempt history
demo/cart.py	Deliberately buggy example application
demo/test_cart.py	Regression test specifying the expected subtotal


Current scope and limitations
- The caller supplies the source and test-file paths; RepoPilot does not yet locate relevant files from a GitHub issue.
- AST duplicate detection catches structurally identical proposals, not all behaviorally equivalent patches.
- Passing tests only establishes correctness for the tested cases; it is not proof of a safe or complete fix.
- Candidate code is temporarily written and executed on the host machine. Do not run RepoPilot on untrusted code or repositories. Production use would require isolated execution with restricted filesystem, network, and credentials.
- Escalation currently produces a local JSON report; it does not notify or assign a human reviewer automatically.
- Historical semantic retrieval with PostgreSQL/pgvector is planned, not implemented.
Next milestones
- Investigate issues to identify relevant files and produce an evidence-based diagnosis before patch generation.
- Retrieve similar resolved investigations using embeddings and PostgreSQL/pgvector, with repository/component-aware reranking.
- Execute candidate patches in an isolated sandbox and improve failure classification.
- Integrate with GitHub issues and produce reviewable patches or pull requests.
- Benchmark patch success rate, retry effectiveness, and false duplicate rejection across a wider test set.
