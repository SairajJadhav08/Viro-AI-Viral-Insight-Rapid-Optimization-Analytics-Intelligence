**1. Top-level user journey (one-line)**

User arrives → hero / marketing → signup / login → Explore / Projects
list → Create Project (upload PDB/CSV/FASTA or choose quick analysis) →
Create triggers processing → Results page shows 3D visualization +
Overview instantly (or within 10s) → detailed panels (Mutation, Drug
Candidates, Modifications) → user saves/marks project status in History
→ Stats, Settings, Profile.

**2. Page-by-page flow (user perspective)**

**2.1 Landing / Hero page (first display)**

-   What user sees: large hero with product name/logo, short tagline,
    primary CTAs: "Get Started" and "Explore Demo". Top nav: Features,
    Pricing, Docs, Login.

-   Primary CTA behaviour:

    -   Get Started → opens Sign Up modal or /signup page.

    -   Explore Demo → opens public "Explore" / sample projects page (no
        auth) with read-only view of example results.

-   Minimal friction: hero shows one screenshot or GIF of the 3D
    protein/antidote visualization to communicate value.

**2.2 Signup / Login**

-   Signup fields: Name, Email, Password, Organization (optional),
    Accept TOS.

-   Optional SSO (Google, institutional SSO) button.

-   On success: auto-login and redirect.

-   After login, call GET /auth/me and GET /orgs/{org}/projects to load
    user data.

**2.3 Explore page (landing after login or via nav)**

-   Purpose: let user browse existing projects (their org's and public
    demos).

-   Layout:

    -   Left: filters (All / My Projects / Demos / Status filter).

    -   Center: project cards (title, type, created_at, status pill).

    -   Right: quick "Create Project" CTA and "Quick Analysis" card
        (pretrained datasets).

-   CTA: Create Project → opens Create Project modal/page.

**2.4 Create Project page (core user form)**

-   Primary sections:

    1.  Project meta: Title, Description, Project Type (e.g.,
        viral-protein, spike-protein), Tags.

    2.  Upload files: PDB (structure), CSV (experimental/assay data),
        FASTA (sequence). Each file card shows required format, sample
        link, and validation.

    3.  Options: Processing profile (Fast/Standard/Deep), Preferred
        units/timezone, Sensitivity for insights (Low/Med/High).

    4.  Quick Analysis card (bottom): same layout & CSS as main create
        card but prefilled: list of pretrained datasets (name,
        description, size, preview). Choosing a pretrained dataset
        auto-fills fields and enables "Create Quick Analysis".

    5.  Buttons: Create Project (primary), Cancel.

-   Upload flow:

    -   For each file, frontend calls POST /orgs/{org}/projects/presign
        → returns pre-signed S3 URL; frontend uploads; then calls POST
        /orgs/{org}/projects/{temp_id}/files with file metadata.

    -   Validate client-side basic checks (extensions, size) and show
        server-side validation result in file card.

-   UX Note: show mapping preview (if CSV has special columns) with a
    small sample table and suggested mapping (columns -\> canonical
    metric names). Allow manual mapping.

**2.5 Create Project action (what happens after user clicks)**

-   Immediately:

    -   Frontend POSTs POST /orgs/{org}/projects with metadata and
        references to uploaded files.

    -   Backend responds with { project_id, status: \"processing\",
        created_at, estimated_wait_seconds: 10 }.

-   UX behaviour:

    -   Redirect to /orgs/{org}/projects/{project_id}/results.

    -   Results page shows a primary loader area with the 3D
        visualization placeholder and a toast: "Analysis started ---
        results will appear instantly or within \~10s."

    -   Polling / socket: frontend starts polling GET
        /orgs/{org}/projects/{project_id}/status every 2s (or maintain
        websocket subscription).

-   Timing rule:

    -   The results/overview information is designed to be **displayed
        instantly** if cached/demo or after very light processing. The
        spec allows a **waiting period up to 10 seconds** to complete
        initial processing for most typical uploads --- this is the
        design expectation to show either instant results or a short
        wait spinner + progress on the Results page.

    -   If processing exceeds 10s, show a progressive loader with steps
        (Uploading → Parsing → Analyzing → Visualizing) and an estimated
        remaining time.

**3. Results page (destination after Create)**

**Route:** /orgs/{org}/projects/{project_id}/results

**Layout (primary visual areas)**

-   Left: vertical toolbar / breadcrumbs. Buttons: Back to Projects,
    Share, Download Results (ZIP), Mark as Completed / Failed (status
    control), Re-run Analysis.

-   Center (main): 3D interactive viewer (protein + antidote
    interaction). Controls: rotate/pan/zoom, color scheme, model
    overlays (binding sites, predicted modifications).

-   Top of center: Overview card (title, status pill, created_at,
    processing time).

-   Below center: Overview of analysis (text summary) + key KPIs
    (binding affinity, predicted efficacy score, confidence %, number of
    mutations found, top drug candidates count, recommended
    modifications count).

-   Right: Tabbed panels (Overview tab active by default; other tabs:
    Mutation, Drug Candidates, Modifications).

-   Bottom (or right dock): Activity feed / change log with system
    suggestions and user notes.

**Immediate behavior on load**

-   If backend returned immediate results: render Overview + 3D viewer
    at once (no wait spinner).

-   If not ready: show skeleton 3D viewer + animated progress bar. When
    results ready (or after up to 10s), seamlessly replace skeleton with
    the rendered 3D model and populate all cards/panels.

**Interaction affordances**

-   Click on residue in 3D viewer → highlights relevant mutation panel
    row and scrolls panel into view.

-   Hover drug candidate → highlights binding pose in 3D viewer.

-   Download: "Export current view as PNG/GLB/PDB" and "Download full
    analysis (JSON/CSV)".

**4. Panels --- Details & fields**

Each panel is a paged table/list + detailed drawer for each item. The
spec below lists required fields for each panel (counts match your
request). Include sorting, filtering, inline search, export.

**4.1 Mutation panel (9 detailed fields per mutation record) --- total
fields = 9**

Each mutation row (and detail view) must include:

1.  **Residue ID** (chain + residue number) --- e.g., A:456

2.  **Original AA** (one-letter) --- e.g., K

3.  **Mutated AA** (one-letter) --- e.g., N

4.  **Position (genomic/protein coord)** --- integer

5.  **Occurrence frequency** --- percentage / count from dataset

6.  **Predicted impact score** --- numeric (0--1) or category
    (neutral/moderate/high)

7.  **Structural context** --- e.g., surface/core/binding-site

8.  **Sequence conservation** --- conservation score (0--1) or
    conservation category

9.  **Notes / suggested follow-up** --- free text / suggestion (e.g.,
    "check for glycosylation change")

UI: show per-row small color-coded impact chip and quick action to "flag
for lab validation".

**4.2 Drug Candidates panel (11 detailed fields per candidate) --- total
fields = 11**

Each drug candidate record should include:

1.  **Candidate ID / Name**

2.  **Molecular formula / SMILES**

3.  **Binding affinity (pred.)** --- kcal/mol or pKd

4.  **Predicted efficacy score** --- 0--100 or 0--1

5.  **Confidence / model support** --- number or label (low/med/high)

6.  **Predicted off-targets** --- short list or count

7.  **ADMET summary** --- simple pass/fail or tier (e.g., low toxicity)

8.  **Synthesis complexity / feasibility** --- categorical / score

9.  **Binding site(s)** --- residue list or region name

10. **Supporting evidence** --- links to assay rows or dataset indices
    (CSV row refs)

11. **Recommendation / next step** --- e.g., "In vitro assay
    suggested" + optional action button

UI: clicking a candidate opens a drawer with 3D visualization overlay
(pose), download button for ligand PDB/SMILES, and "Mark tested"
toggles.

**4.3 Modifications panel (11 detailed fields per modification) ---
total fields = 11**

Each suggested modification (protein engineering or chemical mod) record
includes:

1.  **Modification ID / name**

2.  **Type** --- substitution, insertion, deletion, chemical-mod

3.  **Target residue(s)** --- chain + positions

4.  **Proposed change** --- e.g., "K -\> N" or "Add PEGylation at
    N-term"

5.  **Predicted effect on binding** --- numeric / category

6.  **Predicted effect on stability** --- numeric / category

7.  **Predicted immunogenicity** --- score/flag

8.  **Estimated ease of implementation** --- lab feasibility score

9.  **Suggested protocol notes** --- textual short protocol suggestion

10. **Dependencies / preconditions** --- e.g., "requires removal of
    glycosylation"

11. **Confidence & provenance** --- which model/dataset produced it and
    confidence level

UI: each mod has CTA "Add to experiment plan" and ability to attach
experimental results later.

**5. History & Project status (Projects list / History section)**

-   All created projects appear in /orgs/{org}/projects (History view).
    Project card shows Title, date, status pill: Processing, Completed,
    Failed, Abandoned, Draft.

-   Status semantics:

    -   Processing --- automated analysis ongoing.

    -   Completed --- user has marked as completed (scientist validated
        results or finished experiments).

    -   Failed --- user marked as failed (attempts unsuccessful).

    -   Abandoned --- user left incomplete.

-   Important: **status is user-controlled.** System suggests statuses
    (e.g., upon generating definitive positive candidate list the system
    may recommend \"Ready for Lab\"), but **only user/scientist can set
    Completed/Failed**.

-   Controls on project card / results page:

    -   Mark Completed → PATCH /orgs/{org}/projects/{id} with { status:
        \"completed\", completed_at }

    -   Mark Failed → similar patch with reason required (modal asks
        "Why failed?").

-   Each status change is written into project.history (audit log) for
    traceability.

**6. Overview / User stats & Dashboard**

-   /dashboard (user overview) shows aggregated stats:

    -   Projects created (total / this month)

    -   Success rate (Completed / Total)

    -   Average processing time

    -   Top used pretrained datasets

    -   Recent activity & comments

-   Visualizations: small time-series of projects created, pie chart for
    status distribution, leaderboards (most active users).

-   Clicking stat tiles filters Projects / History to the relevant list.

**7. Settings & Preferences**

-   User settings:

    -   Notification preferences (email/slack/in-app) for new insights,
        job completion, errors.

    -   Default processing profile (Fast/Standard/Deep).

    -   Preferred language, timezone, units.

    -   API key management.

-   Org settings:

    -   Retention policy for projects.

    -   Allowed file types and max upload sizes.

    -   Role & access control (who can mark project status).

-   Settings changes saved via PUT /orgs/{org}/preferences and PUT
    /users/{user_id}/preferences.

**8. My Profile & top-right menu**

-   Top-right avatar drop-down: Profile, Settings, Billing, Help, Sign
    out.

-   Profile page: avatar, name, email, org(s), role, bio, public profile
    toggle (for demo sharing).

-   Quick access: "Create Project" and "My Projects" shortcuts in
    top-right menu.

**9. Quick Analysis card (bottom of Create Project page)**

-   Purpose: allow fast experiments using pre-trained datasets so users
    can get instant sample results without uploading custom files.

-   UX: card visually matches project create card (same CSS/layout). It
    lists pretrained dataset tiles:

    -   Each tile: dataset name, brief description, dataset size, last
        updated, "Run Quick Analysis" CTA.

-   Behavior:

    -   Clicking a tile prepopulates Create Project form (files field
        shows dataset selected) and runs analysis optimized for speed.

    -   Result flow identical to Create Project but usually completes
        **instantly** or well under 5 seconds.

    -   Quick Analysis results also saved as projects (flagged
        quick_analysis: true) so they appear in History.

**10. Notifications, real-time updates & webhooks**

-   Notification types: Job progress, Job complete, Job fail, New
    insights, Share requests.

-   Transport:

    -   Realtime: WebSocket or SSE to push status updates and new
        insights.

    -   Fallback: Polling endpoints (/projects/{id}/status).

    -   Webhooks for orgs: allow external lab systems to receive
        project.completed or insight.generated events.

-   User-configurable channels in Settings.

**11. API mapping (essential endpoints for this flow)**

-   POST /auth/signup

-   POST /auth/login

-   GET /auth/me

-   GET /orgs/{org}/projects (History / Explore)

-   POST /orgs/{org}/projects/presign (file upload presign)

-   POST /orgs/{org}/projects (create new project) → returns {
    project_id, status }

-   GET /orgs/{org}/projects/{project_id}/status

-   GET /orgs/{org}/projects/{project_id}/results (full results payload)

-   GET /orgs/{org}/projects/{project_id}/model-assets/{asset} (download
    PDB/GLB)

-   PATCH /orgs/{org}/projects/{project_id} (update status, metadata)

-   GET /orgs/{org}/datasets/pretrained (list quick analysis datasets)

-   POST /orgs/{org}/projects/{project_id}/re-run (re-run analysis)

-   GET /orgs/{org}/dashboard/overview (user stats)

**12. Data model (core project & results shapes --- JSON example)**

**Project (metadata)**

{

\"project_id\": \"uuid\",

\"org_id\": \"uuid\",

\"title\": \"Spike protein X analysis\",

\"description\": \"Test of PDB/CSV/FASTA\",

\"created_by\": \"user_uuid\",

\"created_at\": \"2025-11-21T10:15:00Z\",

\"status\": \"processing\",

\"files\": \[

{\"type\": \"pdb\", \"path\": \"s3://\.../file.pdb\", \"validated\":
true},

{\"type\": \"csv\", \"path\": \"\...\", \"validated\": true},

{\"type\": \"fasta\", \"path\": \"\...\", \"validated\": true}

\],

\"processing_profile\": \"standard\",

\"quick_analysis\": false

}

**Results (returned by GET /projects/{id}/results)**

{

\"project_id\": \"\...\",

\"overview\": {

\"binding_affinity\": -8.6,

\"efficacy_score\": 0.87,

\"confidence\": 0.92,

\"mutations_count\": 12,

\"drug_candidates_count\": 6,

\"modifications_count\": 4,

\"summary_text\": \"Predicted strong binding at site A with top
candidate Z, recommended modifications to glycosylation sites\...\"

},

\"viewer_asset\": {

\"glb_url\": \"s3://\.../viewer.glb\",

\"annotations\":
\[{\"id\":\"a1\",\"type\":\"binding_site\",\"residues\":\[\...\]}\]

},

\"mutations\": \[ { /\* 9 fields as listed earlier \*/ } \],

\"drug_candidates\": \[ { /\* 11 fields \*/ } \],

\"modifications\": \[ { /\* 11 fields \*/ } \],

\"log\": \[ {\"ts\":\"\...\",\"message\":\"Parsed PDB, mapped 310
residues\"} \],

\"generated_at\": \"2025-11-21T10:15:08Z\"

}

**13. UX states, errors & edge cases**

**Success / happy path**

-   Files valid → project created → results populated instantly or
    within ≤10s → user inspects and marks status.

**Validation errors**

-   Invalid file format → file card shows red error with explanation and
    sample link.

-   Missing mandatory file → CTA disabled with tooltip "Required: PDB".

**Processing failures**

-   If backend fails to parse → results page shows error with actionable
    options: Retry, Contact Support, Download raw logs.

**Timeout / long processing**

-   Processing \> 10s → show progress steps and allow user to opt for
    email notification when complete.

**Concurrency**

-   Multiple projects can be created in parallel. Show queue position if
    backend cannot start immediately.

**14. Acceptance criteria & QA checklist (concrete)**

1.  Create Project: uploading valid PDB, CSV, FASTA should create
    project and redirect to results page within 2s. If analysis
    completes instantly, results visible immediately. If not, initial
    status and progress appear and final results appear within 10s in
    \>90% of test cases for small datasets.

2.  Results correctness: GET /projects/{id}/results returns overview +
    viewer_asset + panels (mutations/drug_candidates/modifications) with
    all required fields populated for generated items.

3.  Interactions:

    -   Clicking mutation/ candidate highlights viewer region and opens
        detail drawer.

    -   Mark Completed / Mark Failed updates status and appears in
        History immediately.

4.  Quick Analysis:

    -   Selecting a pretrained dataset runs analysis and creates project
        flagged quick_analysis: true.

5.  History:

    -   Projects persist, filters/sorts work, status toggles saved to
        audit log.

6.  Exports & Downloads:

    -   Export JSON/CSV/GLB downloads contain expected contents.

7.  Security:

    -   File upload uses pre-signed URLs. Only authenticated users can
        access project assets.

8.  Mobile:

    -   Core flows (Create, View Results, Mark Status) usable on mobile
        with responsive layout and no hidden controls.

**15. Accessibility, performance & telemetry (implementation hints)**

-   Accessibility: ARIA labels for viewer controls and data tables;
    keyboard shortcuts for switching panels; color contrast check.

-   Performance: 3D viewer loads GLB; show low-res fallback while
    high-res loads; lazy-load panels content only when user visits them.

-   Telemetry: instrument events --- project.create, project.complete,
    mutation.view, candidate.download. Capture processing durations and
    failure reasons for monitoring.

**16. Developer handoff checklist (deliverables for front/backend
teams)**

-   UI: mockups for Create Project, Results (desktop + mobile),
    Mutation/Drug/Modification detail drawers.

-   API: full OpenAPI spec for endpoints listed above and sample
    responses.

-   File contract: accepted PDB/CSV/FASTA schemas and sample files.

-   Quick Analysis dataset list (names, short descriptions, GLB assets).

-   Acceptance test suite (E2E) verifying the timing requirements
    (instant or ≤10s experience).
