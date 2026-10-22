# Graph Report - alexavoiceassistant  (2026-10-21)

## Corpus Check
- 209 files · ~1,396,378 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: (none) 3, .css 2, .example 1)

## Summary
- 3147 nodes · 9116 edges · 111 communities (105 shown, 6 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 402 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4a4f25aa`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- archify.mjs
- check-update.mjs
- render-erd.mjs
- generated-validators.mjs
- geometry.mjs
- diagnostics.mjs
- architecture-delta.mjs
- render-class.mjs
- visual-check.mjs
- path-semantics.mjs
- render-architecture.mjs
- render-lifecycle.mjs
- i18n.mjs
- workflow-compiler.mjs
- UKSIWDDN.js
- test_server.py
- render-waterfall.mjs
- generate-brand-marks.mjs
- render-timeline.mjs
- atomic-output.mjs
- createRouter
- server.py
- finalize.mjs
- L4LY553T.js
- brand-marks.mjs
- preview.mjs
- build
- check-render-output.mjs
- row
- render-tree.mjs
- runtime.py
- register_tools
- render.mjs
- YAYTP6L5.js
- func3
- Ledger
- validate.mjs
- route-quality.mjs
- EEIX5ZYH.js
- 42UTT654.js
- compileWorkflowInternal
- IZOKQ2GT.js
- focusEdgeAttrs
- UPTXNAXN.js
- workflow-v2.mjs
- escapeHtml
- diagrams.mjs
- reader.js
- output-path.mjs
- portable-path.mjs
- parseExplainer
- check.mjs
- workflow-compiler.mjs
- test_ledger.py
- laneTop
- config.py
- PipeCdp
- prepare.mjs
- repository-evidence.mjs
- Store
- EJ5KOXYD.js
- parse_kitchen_utterance
- browser-check.mjs
- desktop-readability.mjs
- sources.mjs
- SousChefVoiceApp
- parseAttrs
- scenarios.mjs
- "Sous-Chef": Voice-First Kitchen Inventory, Meal Planning & Nutrition Agent
- collectArrows
- Authoring contract
- ref_node_fs
- authoring-contract.md
- validatePortablePath
- routeBudgetMetrics
- analyzeSvgPath
- charts.mjs
- Delivery contract
- validate20
- manifest.json
- prepareDiagramBrandMarks
- Spoken Amount Parser Engineering Standard
- Explainer authoring
- 🍳 Sous-Chef: Voice-First Kitchen Assistant & Inventory Ledger
- Entity-Relationship Renderer
- Repository-backed authoring
- Viewer Runtime reference
- Workflow Renderer
- FastMCP Server Engineering Standard
- Postgres Ledger Engineering Standard
- captureRemoteBrand
- Event Timeline Renderer
- Recipe Matching Engine Engineering Standard
- Web Voice Companion Engineering Standard
- Sequence Renderer
- Archify JSON IR Schemas
- Third-party notices
- Amazon Bedrock Converse Engineering Standard
- USDA Nutrition Engineering Standard
- 10. Reliability engineering (main focus)
- Architecture layout repair
- Hierarchy and Tree Renderer
- 4. Conversation design
- Authoring defaults
- 5. Functional requirements
- detail
- 7. Architecture
- context_tracker.md
- brand-marks/README.md
- pele/README.md
- update-awareness.md

## God Nodes (most connected - your core abstractions)
1. `compileWorkflowInternal()` - 198 edges
2. `asArray()` - 100 edges
3. `textUnits()` - 76 edges
4. `compileDataflow()` - 71 edges
5. `escapeHtml()` - 69 edges
6. `createRouter()` - 63 edges
7. `build()` - 58 edges
8. `rectsOverlap()` - 54 edges
9. `commandDeliver()` - 47 edges
10. `throwDiagnosticError()` - 41 edges

## Surprising Connections (you probably didn't know these)
- `8. Friction Log` --references--> `Store`  [INFERRED]
  PROJECT_CONTEXT.md → src/sous_chef/ledger.py
- `Lifecycle` --references--> `success()`  [INFERRED]
  .agents/skills/archify/references/authoring-contract.md → src/sous_chef/runtime.py
- `4. Daily Nutrition Summary (`nutrition_summary`)` --references--> `nutrition_summary()`  [INFERRED]
  .agents/skills/usda-nutrition/SKILL.md → src/sous_chef/server.py
- `4. Cook & Deduct Pattern (`cook_recipe`)` --references--> `cook_recipe()`  [INFERRED]
  .agents/skills/recipe-matching-engine/SKILL.md → src/sous_chef/server.py
- `Design rules` --references--> `success()`  [INFERRED]
  .agents/skills/archify/renderers/lifecycle/README.md → src/sous_chef/runtime.py

## Import Cycles
- None detected.

## Communities (111 total, 6 thin omitted)

### Community 0 - "archify.mjs"
Cohesion: 0.06
Nodes (121): acquireDeliveryLock(), artifactCheckMaxBuffer(), artifactIdentity(), assertDeliveryOwnership(), assertOwnedDeliveryLock(), beginDeliveryAttempt(), canonicalExistingDeliveryOutput(), captureDeliveryTargetState() (+113 more)

### Community 1 - "check-update.mjs"
Cohesion: 0.06
Nodes (111): acquireOperation(), assertBoundedRegularFile(), assertCacheTargetAbsent(), assertRenameableCacheEntry(), assertSafeCacheEntry(), assertSafeDirectory(), assertSafeRegularFile(), cacheMkdir() (+103 more)

### Community 2 - "render-erd.mjs"
Cohesion: 0.04
Nodes (84): bandedLayout(), DEFAULT_ER_GRID, entityHeight(), erGridLayout(), gridColumn(), resolvedEntityWidth(), resolveEntityPos(), validateErGridPlacement() (+76 more)

### Community 3 - "generated-validators.mjs"
Cohesion: 0.03
Nodes (73): pattern10, pattern11, pattern12, pattern13, pattern133, pattern14, pattern15, pattern16 (+65 more)

### Community 4 - "geometry.mjs"
Cohesion: 0.10
Nodes (68): validateArchitecture(), validateClassDiagram(), validateDataflow(), validateEr(), validateSequence(), recordDiagnostic(), throwDiagnosticProblems(), anchorFitsCanvas() (+60 more)

### Community 5 - "diagnostics.mjs"
Cohesion: 0.07
Nodes (30): childPath, normalize(), startDeliveryUpdateCheck(), unavailable(), __dirname, loadDiagramWithBrandMarks(), boundaryKey, formatDiagnostics() (+22 more)

### Community 6 - "architecture-delta.mjs"
Cohesion: 0.07
Nodes (66): addNodeMarker(), addState(), annotateArchitectureSideSvg(), architectureDeltaChangeRows(), ArchitectureDeltaError, BOUNDARY_FIELDS, boundaryChangeMap(), boundaryElements() (+58 more)

### Community 7 - "render-class.mjs"
Cohesion: 0.05
Nodes (61): attributeText(), autoViewBox(), bands, busGroups, busPaths, cliArgs, compartments(), connectionEndpointSide() (+53 more)

### Community 8 - "visual-check.mjs"
Cohesion: 0.08
Nodes (57): appendEvidenceCleanupWarning(), appendEvidencePublicationFailure(), backupOwnedPublishedEntry(), baseReceipt(), beginVisualEvidenceWrite(), CAPTURE_VIEWPORTS, CHROME_NO_SANDBOX_ENV, CHROME_STARTUP_TIMEOUT_MS (+49 more)

### Community 9 - "path-semantics.mjs"
Cohesion: 0.15
Nodes (39): visualEvidenceOwnershipMatches(), absolutePath(), compareFutureLocations(), compareKnownEntries(), compareUnmaterializedNames(), containedBy(), futureWindowsNameRisk(), hasStableIdentity() (+31 more)

### Community 10 - "render-architecture.mjs"
Cohesion: 0.05
Nodes (56): DEFAULT_GRID, gridLayout(), resolveComponentPos(), validateGridPlacement(), architectureLegendEntries, autoViewBoxFor(), boundaryLabelWidth(), boundaryRect() (+48 more)

### Community 11 - "render-lifecycle.mjs"
Cohesion: 0.06
Nodes (56): assignArcLevels(), assignTracks(), bracketOf, brackets, bracketTargets, canvasWidth, countCrossings(), depth (+48 more)

### Community 12 - "i18n.mjs"
Cohesion: 0.06
Nodes (57): applyLocaleTranslations(), isFilesystemError(), loadDiagram(), outputPathGuards, RELATIONSHIP_COLLECTIONS, SEMANTIC_COLLECTIONS, START_TYPES, throwOutputError() (+49 more)

### Community 13 - "workflow-compiler.mjs"
Cohesion: 0.06
Nodes (56): ensureAutoLegendFits(), renderLegend(), arrowClass, automaticHeight, compositionFrames, contentBottom, __dirname, layout (+48 more)

### Community 14 - "UKSIWDDN.js"
Cohesion: 0.10
Nodes (38): D(), expect(), fail(), H(), j(), S(), take(), text() (+30 more)

### Community 15 - "test_server.py"
Cohesion: 0.07
Nodes (40): ERD, Schema lookup, Input, Legend presentation contract, Config, call(), db(), _free_port() (+32 more)

### Community 16 - "render-waterfall.mjs"
Cohesion: 0.05
Nodes (46): axisLabels, buildLayoutReport(), byId, children, cliArgs, details, { diagram: wf, template, outPath, sourceEvidence }, __dirname (+38 more)

### Community 17 - "generate-brand-marks.mjs"
Cohesion: 0.04
Nodes (46): bin, archify, description, devDependencies, ajv, simple-icons, engines, node (+38 more)

### Community 18 - "render-timeline.mjs"
Cohesion: 0.06
Nodes (39): breaks, buildLayoutReport(), cards, cliArgs, { diagram: tl, template, outPath, sourceEvidence }, __dirname, durationLabel(), events (+31 more)

### Community 19 - "atomic-output.mjs"
Cohesion: 0.12
Nodes (52): captureOwnedDeliverySidecars(), args, pathEntry(), restoreOwnedBackup(), unlinkOwnedEntry(), backupPublicRegularFileBinding(), captureAtomicOutput(), captureRegularFileBinding() (+44 more)

### Community 20 - "createRouter"
Cohesion: 0.13
Nodes (46): createRouter(), alignFacingPorts(), automaticEndpoint(), cachePath(), candidateSidePairs(), collinearBacktrack(), collinearOverlapLength(), computePath() (+38 more)

### Community 21 - "server.py"
Cohesion: 0.05
Nodes (35): execute_cooking_deduction(), find_recipe_by_id(), get_all_recipes(), _load_seeds(), match_recipes(), calculate_item_macros(), calculate_meal_nutrition(), _load_data() (+27 more)

### Community 22 - "finalize.mjs"
Cohesion: 0.11
Nodes (42): allChecksPassed(), browserEvidence(), captureReceipt(), compactFinalizeReceipt(), consolidateDiagnostics(), defaultFinalizeReceiptPath(), defaultFinalizeSummaryPath(), defaultRunner() (+34 more)

### Community 23 - "L4LY553T.js"
Cohesion: 0.11
Nodes (33): mt(), e(), o(), r(), t(), u(), x(), addPlot() (+25 more)

### Community 24 - "brand-marks.mjs"
Cohesion: 0.11
Nodes (20): BASIC_HTML_REFERENCES, beforeDeadline(), checkedFetch(), COLLECTIONS, decodeIconHref(), HTML_C1_REFERENCES, iconCandidates(), ipv4Private() (+12 more)

### Community 25 - "preview.mjs"
Cohesion: 0.11
Nodes (39): failureDetails(), launchTarget(), launchTimeout(), openArtifact(), OPENERS, openLoopbackUrl(), atomicOutputError(), atomicOutputFailure() (+31 more)

### Community 26 - "build"
Cohesion: 0.10
Nodes (66): busRouteConflict(), compileDataflow(), attempt(), build(), compactCorridors(), crossingFlows(), detourFor(), endpointStubs() (+58 more)

### Community 27 - "check-render-output.mjs"
Cohesion: 0.08
Nodes (21): checks, collectLegendCollisions(), collectRelationshipCrossings(), composition, crossProduct(), ELEMENT_NUMERIC_ATTRS, HTML_VOID_ELEMENTS, htmlPath (+13 more)

### Community 28 - "row"
Cohesion: 0.09
Nodes (25): row(), at(), kind(), Architecture, Class, Dataflow, Lifecycle, Mode placement (+17 more)

### Community 29 - "render-tree.mjs"
Cohesion: 0.07
Nodes (29): all, ancestorsOf(), attachOf(), bandSize, bandStart, centerOf(), childrenOf, cliArgs (+21 more)

### Community 30 - "runtime.py"
Cohesion: 0.11
Nodes (14): icon(), Node icons, Design rules, Input, Layout, Legend and state marks, Lifecycle Renderer, Validation (+6 more)

### Community 31 - "register_tools"
Cohesion: 0.10
Nodes (34): 5. Idempotency Key Handling, 1. Testing Philosophy (Reliability #1), 2. Pytest Fixture Architecture (`tests/conftest.py`), 3. Synthetic DB Outage & Timeout Test, 4. The 25-Phrase Golden Test Set, 5. Implementation Checklist, Reliability & Golden Set Testing Engineering Standard, 9. MCP tool contracts (+26 more)

### Community 32 - "render.mjs"
Cohesion: 0.12
Nodes (26): fileName(), parseExplainerDiff(), fail(), finishHunk(), startFile(), sourceLines(), layoutExplainerPanels(), finish() (+18 more)

### Community 33 - "YAYTP6L5.js"
Cohesion: 0.14
Nodes (31): Ge(), I(), Z(), ae(), be(), Ct(), de(), $e() (+23 more)

### Community 34 - "func3"
Cohesion: 0.09
Nodes (38): func3(), validate27(), validate28(), validate30(), validate31(), validate33(), validate34(), validate36() (+30 more)

### Community 35 - "Ledger"
Cohesion: 0.11
Nodes (9): 6. Non-functional requirements, check_household(), Ledger, body(), LedgerError, normalize_item(), normalize_unit(), parse_ts() (+1 more)

### Community 36 - "validate.mjs"
Cohesion: 0.14
Nodes (26): escapeHtml(), inlineError(), parseInline(), problem(), segment(), referenceFor(), renderInline(), EDGE_KEYS (+18 more)

### Community 37 - "route-quality.mjs"
Cohesion: 0.12
Nodes (27): boundsForPoints(), boundsForRects(), cleanRouteDetourProblems(), collinearOverlap(), DEFAULTS, emptyControlPointClearance(), expandedRect(), inferredSide() (+19 more)

### Community 38 - "EEIX5ZYH.js"
Cohesion: 0.14
Nodes (25): addStyleData(), addSubsetData(), addTextData(), color(), Ct(), dt(), et(), getCurrentSets() (+17 more)

### Community 39 - "42UTT654.js"
Cohesion: 0.15
Nodes (25): addClass(), addPoint(), B(), ct(), Ht(), Kt(), parse(), qt() (+17 more)

### Community 40 - "compileWorkflowInternal"
Cohesion: 0.06
Nodes (108): anchor(), joinRoutePoints(), variantAccent(), compileWorkflowInternal(), authoredPinEvidence(), authoredRouteAssertionFields(), automaticEndpointRepairs(), automaticForwardReversePx() (+100 more)

### Community 41 - "IZOKQ2GT.js"
Cohesion: 0.24
Nodes (19): $t(), f(), bt(), b(), ft(), gt(), j(), lt() (+11 more)

### Community 42 - "focusEdgeAttrs"
Cohesion: 0.13
Nodes (27): renderBoundaryFrame(), renderBoundaryLabel(), renderConnectionLabel(), renderConnectionPath(), renderSvg(), renderMarkerDefs(), renderSvg(), flowStrokeWidth() (+19 more)

### Community 43 - "UPTXNAXN.js"
Cohesion: 0.17
Nodes (21): l(), m(), p(), i(), addLink(), be(), de(), $e() (+13 more)

### Community 44 - "workflow-v2.mjs"
Cohesion: 0.22
Nodes (19): clone(), diagnostic(), expandableViewBox(), legacyLayoutProbe(), legacyRequirementProbe(), migrateWorkflowDocument(), requiredViewBoxFrom(), result() (+11 more)

### Community 45 - "escapeHtml"
Cohesion: 0.15
Nodes (38): componentContext(), renderComponent(), headerHeight(), memberColumns(), memberSpans(), punctuated(), renderMembers(), renderType() (+30 more)

### Community 46 - "diagrams.mjs"
Cohesion: 0.17
Nodes (22): attrs(), changesPreview(), compileExplainerDiagram(), decode(), duplicateCheck(), fail(), freezeBytes(), inferredId() (+14 more)

### Community 47 - "reader.js"
Cohesion: 0.14
Nodes (21): applyTheme(), cropDiagramPreviews(), ensureDiagramReadability(), exportImage(), fitDiagrams(), fitLaneFrames(), layoutBoard(), plan() (+13 more)

### Community 48 - "output-path.mjs"
Cohesion: 0.23
Nodes (20): defaultDeliveryPaths(), authoredOutputDiagnostic(), canonicalFuturePath(), nativeOutputDiagnostic(), OutputPathError, pathIsInside(), rejectWindowsIpcShare(), resolveNativeOutputDirectory() (+12 more)

### Community 49 - "portable-path.mjs"
Cohesion: 0.29
Nodes (12): assertProfile(), classifySemanticCollision(), collisionError(), createSemanticIndex(), findSemanticCollision(), pathError(), PORTABLE_PATH_PROFILES, PortablePathError (+4 more)

### Community 50 - "parseExplainer"
Cohesion: 0.20
Nodes (21): csv(), parseExplainer(), addBlock(), assessment(), attributes(), boolean(), cells(), directive() (+13 more)

### Community 51 - "check.mjs"
Cohesion: 0.19
Nodes (13): checkExplainerHtml(), decode(), decodeURIComponentSafe(), isExplainerHtml(), scanHtml(), packPageBundle(), swap(), unpackPageBundle() (+5 more)

### Community 52 - "workflow-compiler.mjs"
Cohesion: 0.06
Nodes (71): renderNode(), renderStageHeader(), stageHeaderText(), entityHeader(), preferredWidth(), validateStructure(), automaticCanvasWidth(), participantSpreadGeometry() (+63 more)

### Community 53 - "test_ledger.py"
Cohesion: 0.19
Nodes (14): groceries(), led(), store(), test_concurrent_retries_apply_once(), test_concurrent_writes_from_many_connections(), test_event_log_is_append_only(), test_failed_op_rolls_back_whole_batch(), test_households_are_isolated() (+6 more)

### Community 54 - "laneTop"
Cohesion: 0.26
Nodes (15): groupSpan(), measuredContentBounds(), renderGroup(), renderLane(), workflowCompositionFrames(), createWorkflowLaneGeometry(), laneGroupFooterH(), laneGroupHeaderH() (+7 more)

### Community 55 - "config.py"
Cohesion: 0.23
Nodes (6): _bool(), ConfigError, _float(), _int(), _list(), test_config_reads_platform_port()

### Community 56 - "PipeCdp"
Cohesion: 0.21
Nodes (5): browserEnvironment(), ChromeVisualBrowser, chromeVisualBrowserArgs(), evaluate(), PipeCdp

### Community 57 - "prepare.mjs"
Cohesion: 0.24
Nodes (16): assertPreparedDependencies(), digest(), fail(), identity(), parseValidatedExplainer(), prepareExplainer(), readPreparedBundle(), rebindPreparedBundle() (+8 more)

### Community 58 - "repository-evidence.mjs"
Cohesion: 0.25
Nodes (16): EVIDENCE_NODE_COLLECTIONS, evidenceFailure(), evidenceNodes(), gitValue(), hasRepositoryEvidence(), prefetchBlobs(), readBatchObjects(), runGit() (+8 more)

### Community 60 - "EJ5KOXYD.js"
Cohesion: 0.28
Nodes (15): A(), b(), d(), E(), indent(), k(), L(), N() (+7 more)

### Community 61 - "parse_kitchen_utterance"
Cohesion: 0.15
Nodes (17): _extract_qty_and_unit(), _find_unit(), parse_kitchen_utterance(), ParsedItem, ParseResult, test_confirm_action_intents(), test_consume_action_detected(), test_explicit_quantities_parsed_accurately() (+9 more)

### Community 62 - "browser-check.mjs"
Cohesion: 0.26
Nodes (14): activate(), evaluate(), EXPLAINER_VIEWPORTS, explainerObservation(), explainerObservationDiagnostics(), expression(), inspectExplainerBrowser(), inspectNativePreviewLayout() (+6 more)

### Community 63 - "desktop-readability.mjs"
Cohesion: 0.13
Nodes (16): DECLARED_WIDE_READER_CONTRACT, DECLARED_WIDE_READER_MAX_WIDTH, DECLARED_WIDE_READER_RATIO, DECLARED_WIDE_REFERENCE_BODY_HORIZONTAL_PX, DECLARED_WIDE_REFERENCE_DIAGRAM_HORIZONTAL_PX, declaredWideReadabilityBudget(), describeFixedWidthOverflow(), DESKTOP_FIXED_VERTICAL_CHROME_PX (+8 more)

### Community 64 - "sources.mjs"
Cohesion: 0.29
Nodes (16): chartFromData(), compileExplainerChart(), pieLegend(), containsExplainerSecret(), deriveRepository(), digest(), fail(), gitBytes() (+8 more)

### Community 65 - "SousChefVoiceApp"
Cohesion: 0.15
Nodes (4): CookingMusicEngine, escapeHtml(), formatDisplayQty(), SousChefVoiceApp

### Community 66 - "parseAttrs"
Cohesion: 0.27
Nodes (14): collectArchitectureLeadingSpace(), collectLegendBoxes(), collectRelationshipLabelMasks(), collectSequenceColumnSpace(), collectSequenceNoteBorders(), collectUntransformedNodeRects(), legendTextWidth(), numberAttr() (+6 more)

### Community 67 - "scenarios.mjs"
Cohesion: 0.24
Nodes (10): detectGuideLanguage(), formatScenarioList(), listScenarioRecipes(), localized(), normalized(), publicGuideData(), RAW_RECIPES, recommendScenario() (+2 more)

### Community 68 - ""Sous-Chef": Voice-First Kitchen Inventory, Meal Planning & Nutrition Agent"
Cohesion: 0.08
Nodes (24): 0. Instructions for the AI assistant reading this document, 11. Recipe matching algorithm, 12. Nutrition, 13. AI / LLM strategy, 14. Security, privacy and compliance, 15. Observability and operations, 16.1 Tests, 16.2 Success metrics (+16 more)

### Community 69 - "collectArrows"
Cohesion: 0.22
Nodes (11): attrEntries(), collectArrows(), collectCompositionFrames(), collectNonFiniteAttrs(), continuousRoutePoints(), decodeNumericReferences(), inspectedPath(), isNumericAttr() (+3 more)

### Community 70 - "Authoring contract"
Cohesion: 0.12
Nodes (16): Authoring contract, Composition repair, Engineering profile default, Executable geometry rules, Explicit `via` coordinates, Hand-placed fallback, Label repair, Language consistency (+8 more)

### Community 71 - "ref_node_fs"
Cohesion: 0.33
Nodes (5): createOwnedTempDirectory(), remove(), directoryIdentity(), retryable, verifyIdentity()

### Community 72 - "authoring-contract.md"
Cohesion: 0.22
Nodes (3): Bundled Viewer catalogs, Agent decision path, Brand marks

### Community 73 - "validatePortablePath"
Cohesion: 0.18
Nodes (24): Compact native diagrams, architecture(), classDiagram(), dataflow(), erd(), explainer(), lifecycle(), sequence() (+16 more)

### Community 74 - "routeBudgetMetrics"
Cohesion: 0.29
Nodes (7): routeBudgetMetrics(), segmentPosition(), routeParts(), subpathBudgetMetrics(), subpathCorridors(), subpathLabelClearance(), subpathRhythmIssues()

### Community 75 - "analyzeSvgPath"
Cohesion: 0.53
Nodes (4): analyzeSvgPath(), ARITY, failure(), tokenize()

### Community 76 - "charts.mjs"
Cohesion: 0.14
Nodes (6): NATIVE, k(), M(), O(), v(), width()

### Community 77 - "Delivery contract"
Cohesion: 0.17
Nodes (12): A new candidate at an existing output path, Automated browser evidence, Delivery contract, Failed finalize and candidate repair, Handoff receipt, Last-Good Live Preview, Optional capture evidence, Optional opening (+4 more)

### Community 78 - "validate20"
Cohesion: 0.67
Nodes (3): validate20(), validate22(), validate24()

### Community 80 - "prepareDiagramBrandMarks"
Cohesion: 0.21
Nodes (12): asUrl(), captureBrandReference(), captureTimeoutMilliseconds(), domainMark(), findBrandMark(), lookupForms(), mapConcurrent(), normalizeBrandSourceUrl() (+4 more)

### Community 81 - "Spoken Amount Parser Engineering Standard"
Cohesion: 0.18
Nodes (10): 1. Principles, 2. Spoken Fraction & Colloquial Quantities Table, 3. Unit Conversion Ratios to Base Units, 4. Ambiguity Resolution (Single Clarifying Question), 5. Spoken Readback Formatter, 6. Implementation Checklist, Count (Base Unit: `count`), Mass (Base Unit: `g`) (+2 more)

### Community 82 - "Explainer authoring"
Cohesion: 0.18
Nodes (10): Charts, Choose the form by the shape of the information, Delivery, Draft, Explainer authoring, Inline links and sources, Panel replacement, Panels and layout (+2 more)

### Community 83 - "🍳 Sous-Chef: Voice-First Kitchen Assistant & Inventory Ledger"
Cohesion: 0.18
Nodes (10): 1. Prerequisites, 2. Setup Environment, 3. Database Initialization, 4. Run the FastMCP & Web Companion Server, 🏗️ Architecture, 🌟 Key Features, 📄 License, 🚀 Quickstart (+2 more)

### Community 84 - "Entity-Relationship Renderer"
Cohesion: 0.29
Nodes (6): Cardinality ink, Domain bands, Entity-Relationship Renderer, Reading a schema, The legend band, Typography

### Community 85 - "Repository-backed authoring"
Cohesion: 0.22
Nodes (8): Repository evidence, Directive reference, Author from evidence, Choose an example by structure, Evidence by diagram type, Explore on demand, Repository-backed authoring, line()

### Community 86 - "Viewer Runtime reference"
Cohesion: 0.22
Nodes (8): Canonical exports, Embedded reading addresses, Exploration, Motion and presentation, Reach Share Card, Route Share Card, Truth boundary, Viewer Runtime reference

### Community 87 - "Workflow Renderer"
Cohesion: 0.22
Nodes (9): Design Rules, Fixed v1, Input, Layout contracts, Legend, Migration and layout receipt, Optional semantic checks, Readable v2 (+1 more)

### Community 88 - "FastMCP Server Engineering Standard"
Cohesion: 0.22
Nodes (8): 1. Pinned Dependencies & Transports, 2. Mandatory Reliability Wrapper (Decisions D3 & D4), 3. Strict Response Envelope (PDD Section 9 & Decision D3), 4. Health Checks (Decision D9), 6. Implementation Checklist, Error Response:, FastMCP Server Engineering Standard, Success Response:

### Community 89 - "Postgres Ledger Engineering Standard"
Cohesion: 0.22
Nodes (8): 1. Core Invariants (P0 Foundation), 2. Concurrency & Advisory Locks, 3. Session Timezone Pinning (Friction Log F1), 4. Base Units & Strict Math, 5. Idempotent Batches, 6. Implementation Checklist, Postgres Ledger Engineering Standard, Rules:

### Community 90 - "captureRemoteBrand"
Cohesion: 0.40
Nodes (6): captureRemoteBrand(), imageData(), readHtmlHeadLinks(), readLimited(), remoteBrand(), validIcoImageRanges()

### Community 91 - "Event Timeline Renderer"
Cohesion: 0.40
Nodes (4): Axis, Cards, Event Timeline Renderer, Tested size

### Community 92 - "Recipe Matching Engine Engineering Standard"
Cohesion: 0.25
Nodes (7): 1. Principles, 2. Hard Exclusion Filters, 3. Deterministic Scoring Formula, 4. Cook & Deduct Pattern (`cook_recipe`), 5. Seed Recipes (~10 R1 Recipes), 6. Implementation Checklist, Recipe Matching Engine Engineering Standard

### Community 93 - "Web Voice Companion Engineering Standard"
Cohesion: 0.25
Nodes (7): 1. Aesthetic & UI Architecture, 2. Animated Voice Orb (Alexa-Style State Indicator), 3. Web Speech API Integration (STT & TTS), 4. Live Inventory & Expiring Badge UI, 5. Direct Streamable HTTP MCP Client, 6. Implementation Checklist, Web Voice Companion Engineering Standard

### Community 94 - "Sequence Renderer"
Cohesion: 0.29
Nodes (6): Column fit, Design Rules, Input, Layout budget, Legend, Sequence Renderer

### Community 95 - "Archify JSON IR Schemas"
Cohesion: 0.29
Nodes (7): Archify JSON IR Schemas, Error format, Files, Runtime validation, schema_version policy, Shared definitions (common.schema.json), Visual quality and engineering truth

### Community 96 - "Third-party notices"
Cohesion: 0.29
Nodes (6): JetBrains Mono, No additional rights granted, OpenAI mark, Pele, Simple Icons, Third-party notices

### Community 97 - "Amazon Bedrock Converse Engineering Standard"
Cohesion: 0.29
Nodes (6): 1. Role in Sous-Chef (R1 Scope & AWS Builder Mini-Challenge), 2. Model Selection & Region, 3. Boto3 Converse API Pattern, 4. Deterministic Offline Fallback, 5. Implementation Checklist, Amazon Bedrock Converse Engineering Standard

### Community 98 - "USDA Nutrition Engineering Standard"
Cohesion: 0.29
Nodes (6): 1. Principles & Normalization, 2. Seed Ingredient Table (~50 Core Items), 3. Macro Calculation Algorithm, 4. Daily Nutrition Summary (`nutrition_summary`), 5. Implementation Checklist, USDA Nutrition Engineering Standard

### Community 99 - "10. Reliability engineering (main focus)"
Cohesion: 0.29
Nodes (7): 10.1 Data correctness, 10.2 AI grounding, 10.3 Never guess, 10.4 Graceful failure, 10.5 Drift control, 10.6 Backups and recovery, 10. Reliability engineering (main focus)

### Community 100 - "Architecture layout repair"
Cohesion: 0.50
Nodes (4): Architecture layout repair, Choose the repair scope, One coherent repair, directCorridorBlockers()

### Community 102 - "Hierarchy and Tree Renderer"
Cohesion: 0.29
Nodes (6): Expand and collapse, Hierarchy and Tree Renderer, Input, Layout, Structure checks, Tested size

### Community 104 - "4. Conversation design"
Cohesion: 0.33
Nodes (6): 4.1 Channels, 4.2 Persona and voice rules, 4.3 Key flows, 4.4 Failure flows, 4.5 Proactive behavior, 4. Conversation design

### Community 105 - "Authoring defaults"
Cohesion: 0.40
Nodes (5): Authoring defaults, Composition and meaning, Evidence and schema, Layout and routing, Presentation and modes

### Community 107 - "5. Functional requirements"
Cohesion: 0.40
Nodes (5): 5. Functional requirements, Cooking and nutrition, Inventory, Platform, Recipes

### Community 109 - "detail"
Cohesion: 0.29
Nodes (6): Waterfall, detail(), Execution Waterfall Renderer, Input, Layout, Tested size

### Community 111 - "7. Architecture"
Cohesion: 0.50
Nodes (4): 7.1 Components, 7.2 Key design choices, 7.3 Model gateway (R3), 7. Architecture

## Knowledge Gaps
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `success()` connect `runtime.py` to `row`, `test_server.py`?**
  _High betweenness centrality (0.111) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `compileWorkflowInternal()` (e.g. with `acceptsFix()` and `compareCost()`) actually correct?**
  _`compileWorkflowInternal()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Should `archify.mjs` be split into smaller, more focused modules?**
  _Cohesion score 0.057309307681885926 - nodes in this community are weakly interconnected._
- **Why does `icon()` connect `runtime.py` to `render.mjs`, `validatePortablePath`?**
  _High betweenness centrality (0.085) - this node is a cross-community bridge._
- **Should `check-update.mjs` be split into smaller, more focused modules?**
  _Cohesion score 0.05570291777188329 - nodes in this community are weakly interconnected._
- **Should `render-erd.mjs` be split into smaller, more focused modules?**
  _Cohesion score 0.04231974921630094 - nodes in this community are weakly interconnected._
- **Should `generated-validators.mjs` be split into smaller, more focused modules?**
  _Cohesion score 0.02702702702702703 - nodes in this community are weakly interconnected._