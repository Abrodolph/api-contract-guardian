**User:**

<task>
Help me create a custom Bob mode called "contract-guardian". 

Role: An API governance specialist who analyzes OpenAPI spec changes and classifies them with zero ambiguity.

roleDefinition: "You are an API contract governance specialist. Your sole function is to compare two OpenAPI specifications and classify the change as BREAKING, SAFE, or REVIEW based on strict rules. You output only valid JSON matching the verdict schema. Never add prose, explanation, or markdown around the JSON."

customInstructions — apply these rules exactly:

BREAKING (any of these = BREAKING):
- A response field is removed or renamed
- A required request field is added
- A field type changes (e.g. string → integer)
- An endpoint path changes
- An HTTP method changes
- A previously optional field becomes required

SAFE (any of these = SAFE):
- An optional query parameter is added
- A new response field is added
- A new endpoint is added
- A new optional request field is added
- A description or documentation-only change

REVIEW (requires human judgment):
- An enum value is removed
- A field changes from nullable to non-nullable
- A default value changes
- A type widens (e.g. integer → number)

Output rules (critical):
- Output ONLY a JSON object. No text before it. No text after it. No markdown code fences.
- The JSON must exactly match this schema:
{
  "verdict": "BREAKING | SAFE | REVIEW",
  "change_summary": "string",
  "affected_field": "string | null",
  "blast_radius": {
    "consumers": [],
    "total_call_sites": 0
  },
  "reasoning": "string"
}
- blast_radius stays empty for now (will be populated by MCP tools later)
- If multiple changes exist, use the most severe verdict

Restrict tools to read-only file access plus any registered MCP tools.
</task>
<environment_details>
# VSCode Visible Files
engine\verdict_schema.json

# VSCode Open Tabs
engine/verdict_schema.json

# Current Time
Current time in ISO 8601 UTC format: 2026-05-17T11:07:43.096Z
User time zone: Asia/Calcutta, UTC+5:30

# Current Cost
$0.00

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>advanced</slug>
<name>🛠️ Advanced</name>


# Current Workspace Directory (c:/Personal/Code/api-contract-guardian) Files
.gitignore
README.md
.claude/
backend/
backend/.gitkeep
bob_sessions/
bob_sessions/.gitkeep
cloud/
cloud/.gitkeep
engine/
engine/verdict_schema.json
frontend/
frontend/.gitkeep
mcp-server/
mcp-server/.gitkeep
mock-api/
mock-api/.gitkeep
mock-api/main.py
mock-api/openapi_baseline.json
mock-api/openapi.json
mock-api/README.md
mock-api/requirements.txt
mock-api/app/
mock-api/app/__init__.py
mock-api/app/main.py
mock-consumers/
mock-consumers/.gitkeep
presentation/
presentation/.gitkeep
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

I'll help you create a custom Bob mode called "contract-guardian" for API governance. Let me start by fetching the instructions for creating a mode.

<fetch_instructions>
<task>create_mode</task>
</fetch_instructions>

---

**User:**

[fetch_instructions for 'create_mode'] Result:

Custom modes can be configured in two ways:
  1. Globally via 'c:\Users\saini\AppData\Roaming\IBM Bob\User\globalStorage\ibm.bob-code\settings\custom_modes.yaml' (created automatically on startup)
  2. Per-workspace via '.bob/custom_modes.yaml' in the workspace root directory

When modes with the same slug exist in both files, the workspace-specific .bob/custom_modes.yaml version takes precedence. This allows projects to override global modes or define project-specific modes.


If asked to create a project mode, create it in .bob/custom_modes.yaml in the workspace root. If asked to create a global mode, use the global custom modes file.

- The following fields are required and must not be empty:
  * slug: A valid slug (lowercase letters, numbers, and hyphens). Must be unique, and shorter is better.
  * name: The display name for the mode
  * roleDefinition: A detailed description of the mode's role and capabilities
  * groups: Array of allowed tool groups (can be empty). Each group can be specified either as a string (e.g., "edit" to allow editing any file) or with file restrictions (e.g., ["edit", { fileRegex: "\.md$", description: "Markdown files only" }] to only allow editing markdown files)

- The following fields are optional but highly recommended:
  * description: A short, human-readable description of what this mode does (5 words)
  * whenToUse: A clear description of when this mode should be selected and what types of tasks it's best suited for. This helps the Orchestrator mode make better decisions.
  * customInstructions: Additional instructions for how the mode should operate

- For multi-line text, include newline characters in the string like "This is the first line.\nThis is the next line.\n\nThis is a double line break."

Both files should follow this structure (in YAML format):

customModes:
  - slug: designer  # Required: unique slug with lowercase letters, numbers, and hyphens
    name: Designer  # Required: mode display name
    description: UI/UX design systems expert  # Optional but recommended: short description (5 words)
    roleDefinition: >-
      You are Bob, a UI/UX expert specializing in design systems and frontend development. Your expertise includes:
      - Creating and maintaining design systems
      - Implementing responsive and accessible web interfaces
      - Working with CSS, HTML, and modern frontend frameworks
      - Ensuring consistent user experiences across platforms  # Required: non-empty
    whenToUse: >-
      Use this mode when creating or modifying UI components, implementing design systems,
      or ensuring responsive web interfaces. This mode is especially effective with CSS,
      HTML, and modern frontend frameworks.  # Optional but recommended
    groups:  # Required: array of tool groups (can be empty)
      - read     # Read files group (read_file, fetch_instructions, search_files, list_files, list_code_definition_names)
      - edit     # Edit files group (apply_diff, write_to_file) - allows editing any file
      # Or with file restrictions:
      # - - edit
      #   - fileRegex: \.md$
      #     description: Markdown files only  # Edit group that only allows editing markdown files
      - browser  # Browser group (browser_action)
      - command  # Command group (execute_command)
      - mcp      # MCP group (use_mcp_tool, access_mcp_resource)
    customInstructions: Additional instructions for the Designer mode  # Optional
<environment_details>
# VSCode Visible Files
engine\verdict_schema.json

# VSCode Open Tabs
engine/verdict_schema.json

# Current Time
Current time in ISO 8601 UTC format: 2026-05-17T11:08:02.086Z
User time zone: Asia/Calcutta, UTC+5:30

# Current Cost
$0.04

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>advanced</slug>
<name>🛠️ Advanced</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

Now I'll create the custom mode for contract-guardian. First, let me check if a `.bob` directory exists in the workspace.

<list_files>
<path>.</path>
<recursive>false</recursive>
</list_files>

---

**User:**

[list_files for '.'] Result:
.gitignore
README.md
.claude/
backend/
bob_sessions/
cloud/
engine/
frontend/
mcp-server/
mock-api/
mock-consumers/
presentation/
<environment_details>
# VSCode Visible Files
engine\verdict_schema.json

# VSCode Open Tabs
engine/verdict_schema.json

# Current Time
Current time in ISO 8601 UTC format: 2026-05-17T11:08:11.789Z
User time zone: Asia/Calcutta, UTC+5:30

# Current Cost
$0.07

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>advanced</slug>
<name>🛠️ Advanced</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

I need to create the `.bob` directory and the `custom_modes.yaml` file. Let me create the custom mode configuration:

<write_to_file>
<path>.bob/custom_modes.yaml</path>
<content>customModes:
  - slug: contract-guardian
    name: 🛡️ Contract Guardian
    description: API contract governance and change analysis
    roleDefinition: >-
      You are an API contract governance specialist. Your sole function is to compare two OpenAPI specifications and classify the change as BREAKING, SAFE, or REVIEW based on strict rules. You output only valid JSON matching the verdict schema. Never add prose, explanation, or markdown around the JSON.
    whenToUse: >-
      Use this mode when analyzing OpenAPI specification changes to determine their impact on API consumers.
      This mode classifies changes with zero ambiguity into BREAKING, SAFE, or REVIEW categories based on
      strict governance rules. It outputs structured JSON verdicts for automated API governance workflows.
    groups:
      - read
      - mcp
    customInstructions: >-
      Apply these classification rules exactly:


      BREAKING (any of these = BREAKING):

      - A response field is removed or renamed

      - A required request field is added

      - A field type changes (e.g. string → integer)

      - An endpoint path changes

      - An HTTP method changes

      - A previously optional field becomes required


      SAFE (any of these = SAFE):

      - An optional query parameter is added

      - A new response field is added

      - A new endpoint is added

      - A new optional request field is added

      - A description or documentation-only change


      REVIEW (requires human judgment):

      - An enum value is removed

      - A field changes from nullable to non-nullable

      - A default value changes

      - A type widens (e.g. integer → number)


      Output rules (critical):

      - Output ONLY a JSON object. No text before it. No text after it. No markdown code fences.

      - The JSON must exactly match this schema:

      {
        "verdict": "BREAKING | SAFE | REVIEW",
        "change_summary": "string",
        "affected_field": "string | null",
        "blast_radius": {
          "consumers": [],
          "total_call_sites": 0
        },
        "reasoning": "string"
      }

      - blast_radius stays empty for now (will be populated by MCP tools later)

      - If multiple changes exist, use the most severe verdict (BREAKING > REVIEW > SAFE)

      - Never include explanatory text, markdown formatting, or conversational responses

      - Your entire response must be parseable as valid JSON
</content>
<line_count>62</line_count>
</write_to_file>

---

**User:**

[write_to_file for '.bob/custom_modes.yaml'] Result:
<file_write_result>
<path>.bob/custom_modes.yaml</path>
<operation>created</operation>
<notice>
<i>You do not need to re-read the file, as you have seen all changes</i>
<i>Proceed with the task using these changes as the new baseline.</i>
</notice>
</file_write_result>

<environment_details>
# VSCode Visible Files
.bob\custom_modes.yaml

# VSCode Open Tabs
.bob/custom_modes.yaml

# Current Time
Current time in ISO 8601 UTC format: 2026-05-17T11:08:25.170Z
User time zone: Asia/Calcutta, UTC+5:30

# Current Cost
$0.11

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>advanced</slug>
<name>🛠️ Advanced</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

<attempt_completion>
<result>
Custom Bob mode "contract-guardian" created successfully at [`.bob/custom_modes.yaml`](.bob/custom_modes.yaml:1)

Key features:
- **Slug**: `contract-guardian`
- **Name**: 🛡️ Contract Guardian
- **Tool Access**: Read-only file operations + MCP tools
- **Classification Rules**: Strict BREAKING/SAFE/REVIEW categorization
- **Output Format**: Pure JSON matching the verdict schema in [`engine/verdict_schema.json`](engine/verdict_schema.json:1)

The mode will automatically appear in Bob's mode selector after reloading the window. It enforces zero-ambiguity API change classification with structured JSON output for automated governance workflows.
</result>
</attempt_completion>

