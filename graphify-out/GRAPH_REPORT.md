# Graph Report - alexavoiceassistant  (2026-10-21)

## Corpus Check
- 208 files · ~1,392,294 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: (none) 3, .css 2, .example 1)

## Summary
- 3131 nodes · 9069 edges · 116 communities (110 shown, 6 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 397 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `198f4db7`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- archify.mjs
- check-update.mjs
- render-erd.mjs
- generated-validators.mjs
- geometry.mjs
- cli.mjs
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
- createReadableLayout
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
- ref_node_url
- UPTXNAXN.js
- workflow-v2.mjs
- validateReadablePinnedGeometry
- diagrams.mjs
- reader.js
- anchor
- portable-path.mjs
- parseExplainer
- check.mjs
- laneTop
- test_ledger.py
- diagnostics.mjs
- config.py
- PipeCdp
- prepare.mjs
- repository-evidence.mjs
- pathFor
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
- render-explainer.mjs
- authoring-contract.md
- validatePortablePath
- open-artifact.mjs
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
- parseExplainerDiff
- Lifecycle Renderer
- Recipe Matching Engine Engineering Standard
- Web Voice Companion Engineering Standard
- Sequence Renderer
- Archify JSON IR Schemas
- Third-party notices
- Amazon Bedrock Converse Engineering Standard
- USDA Nutrition Engineering Standard
- 10. Reliability engineering (main focus)
- captureRemoteBrand
- engineering-profiles.mjs
- Hierarchy and Tree Renderer
- Reliability & Golden Set Testing Engineering Standard
- 4. Conversation design
- Authoring defaults
- validateSchema
- 5. Functional requirements
- Architecture layout repair
- Execution Waterfall Renderer
- proposeWorkflowPlacement
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
- `Design rules` --references--> `success()`  [INFERRED]
  .agents/skills/archify/renderers/lifecycle/README.md → src/sous_chef/runtime.py
- `4. Daily Nutrition Summary (`nutrition_summary`)` --references--> `nutrition_summary()`  [INFERRED]
  .agents/skills/usda-nutrition/SKILL.md → src/sous_chef/server.py
- `4. Cook & Deduct Pattern (`cook_recipe`)` --references--> `cook_recipe()`  [INFERRED]
  .agents/skills/recipe-matching-engine/SKILL.md → src/sous_chef/server.py

## Import Cycles
- None detected.

## Communities (116 total, 6 thin omitted)

### Community 0 - "archify.mjs"
Cohesion: 0.05
Nodes (126): acquireDeliveryLock(), artifactCheckMaxBuffer(), artifactIdentity(), assertDeliveryOwnership(), assertOwnedDeliveryLock(), beginDeliveryAttempt(), canonicalExistingDeliveryOutput(), captureDeliveryTargetState() (+118 more)

### Community 1 - "check-update.mjs"
Cohesion: 0.06
Nodes (111): acquireOperation(), assertBoundedRegularFile(), assertCacheTargetAbsent(), assertRenameableCacheEntry(), assertSafeCacheEntry(), assertSafeDirectory(), assertSafeRegularFile(), cacheMkdir() (+103 more)

### Community 2 - "render-erd.mjs"
Cohesion: 0.04
Nodes (91): renderConnectionPath(), connectionEndpointSide(), pathFor(), buildLayoutReport(), bandedLayout(), DEFAULT_ER_GRID, entityHeight(), erGridLayout() (+83 more)

### Community 3 - "generated-validators.mjs"
Cohesion: 0.03
Nodes (73): pattern10, pattern11, pattern12, pattern13, pattern133, pattern14, pattern15, pattern16 (+65 more)

### Community 4 - "geometry.mjs"
Cohesion: 0.06
Nodes (120): validateArchitecture(), busRouteConflict(), compileDataflow(), attempt(), build(), compactCorridors(), crossingFlows(), detourFor() (+112 more)

### Community 5 - "cli.mjs"
Cohesion: 0.12
Nodes (29): __dirname, applyLocaleTranslations(), isFilesystemError(), loadDiagram(), loadDiagramWithBrandMarks(), outputPathGuards, RELATIONSHIP_COLLECTIONS, SEMANTIC_COLLECTIONS (+21 more)

### Community 6 - "architecture-delta.mjs"
Cohesion: 0.07
Nodes (66): addNodeMarker(), addState(), annotateArchitectureSideSvg(), architectureDeltaChangeRows(), ArchitectureDeltaError, BOUNDARY_FIELDS, boundaryChangeMap(), boundaryElements() (+58 more)

### Community 7 - "render-class.mjs"
Cohesion: 0.05
Nodes (69): attributeText(), autoViewBox(), bands, busGroups, busPaths, cliArgs, compartments(), connectionEndpointSide() (+61 more)

### Community 8 - "visual-check.mjs"
Cohesion: 0.08
Nodes (54): appendEvidenceCleanupWarning(), appendEvidencePublicationFailure(), baseReceipt(), beginVisualEvidenceWrite(), CAPTURE_VIEWPORTS, CHROME_NO_SANDBOX_ENV, CHROME_STARTUP_TIMEOUT_MS, contactSheetHtml() (+46 more)

### Community 9 - "path-semantics.mjs"
Cohesion: 0.11
Nodes (53): visualEvidenceOwnershipMatches(), authoredOutputDiagnostic(), nativeOutputDiagnostic(), rejectWindowsIpcShare(), resolveNativeOutputDirectory(), throwNativeOutputDiagnostic(), validateNativeOutputPath(), validateWindowsNativeComponent() (+45 more)

### Community 10 - "render-architecture.mjs"
Cohesion: 0.06
Nodes (49): DEFAULT_GRID, gridLayout(), resolveComponentPos(), validateGridPlacement(), architectureLegendEntries, autoViewBoxFor(), boundaryLabelWidth(), buildLayoutReport() (+41 more)

### Community 11 - "render-lifecycle.mjs"
Cohesion: 0.04
Nodes (118): componentContext(), renderBoundaryFrame(), renderBoundaryLabel(), renderComponent(), renderConnectionLabel(), renderSvg(), renderType(), renderNode() (+110 more)

### Community 12 - "i18n.mjs"
Cohesion: 0.12
Nodes (26): BUNDLED_CATALOGS, bundledCatalog(), bundledLocaleFor(), CANONICAL_KEYS, CANONICAL_PLACEHOLDERS, catalogFor(), classifyTranslations(), DEFAULT_LOCALE (+18 more)

### Community 13 - "workflow-compiler.mjs"
Cohesion: 0.05
Nodes (105): boundaryRect(), ensureAutoLegendFits(), renderLegend(), autoViewBox(), legendLayout(), preferredWidth(), validateStructure(), arrowClass (+97 more)

### Community 14 - "UKSIWDDN.js"
Cohesion: 0.09
Nodes (31): D(), expect(), fail(), H(), j(), S(), take(), text() (+23 more)

### Community 15 - "test_server.py"
Cohesion: 0.07
Nodes (36): Schema lookup, Legend presentation contract, Config, call(), db(), _free_port(), init_only(), LiveServer (+28 more)

### Community 16 - "render-waterfall.mjs"
Cohesion: 0.05
Nodes (46): axisLabels, byId, children, cliArgs, details, { diagram: wf, template, outPath, sourceEvidence }, __dirname, footprint (+38 more)

### Community 17 - "generate-brand-marks.mjs"
Cohesion: 0.04
Nodes (46): bin, archify, description, devDependencies, ajv, simple-icons, engines, node (+38 more)

### Community 18 - "render-timeline.mjs"
Cohesion: 0.06
Nodes (45): breaks, buildLayoutReport(), cards, cliArgs, clockLabel(), { diagram: tl, template, outPath, sourceEvidence }, __dirname, durationLabel() (+37 more)

### Community 19 - "atomic-output.mjs"
Cohesion: 0.13
Nodes (53): captureOwnedDeliverySidecars(), args, backupOwnedPublishedEntry(), cleanupStagedEvidence(), commitVisualEvidence(), identityMatches(), restoreOwnedBackup(), unlinkOwnedEntry() (+45 more)

### Community 20 - "createRouter"
Cohesion: 0.13
Nodes (45): createRouter(), alignFacingPorts(), automaticEndpoint(), cachePath(), candidateSidePairs(), collinearBacktrack(), collinearOverlapLength(), computePath() (+37 more)

### Community 21 - "server.py"
Cohesion: 0.05
Nodes (26): Store, execute_cooking_deduction(), find_recipe_by_id(), get_all_recipes(), _load_seeds(), match_recipes(), calculate_item_macros(), calculate_meal_nutrition() (+18 more)

### Community 22 - "finalize.mjs"
Cohesion: 0.11
Nodes (43): allChecksPassed(), browserEvidence(), captureReceipt(), compactFinalizeReceipt(), consolidateDiagnostics(), defaultDeliveryPaths(), defaultFinalizeReceiptPath(), defaultFinalizeSummaryPath() (+35 more)

### Community 23 - "L4LY553T.js"
Cohesion: 0.11
Nodes (30): $t(), i(), o(), t(), u(), addPlot(), Je(), K() (+22 more)

### Community 24 - "brand-marks.mjs"
Cohesion: 0.11
Nodes (19): BASIC_HTML_REFERENCES, beforeDeadline(), checkedFetch(), COLLECTIONS, decodeIconHref(), HTML_C1_REFERENCES, iconCandidates(), ipv4Private() (+11 more)

### Community 25 - "preview.mjs"
Cohesion: 0.14
Nodes (33): atomicOutputError(), atomicOutputFailure(), captureOwnedDirectory(), cleanupOwnedDirectory(), cliPath, compactMessage(), diagramTypes, here (+25 more)

### Community 26 - "createReadableLayout"
Cohesion: 0.21
Nodes (14): authoredNodeHeight(), authoredNodeWidth(), canonicalReadableWorkflow(), compareWorkflowEdges(), repointReferences(), unknownIdReferenceFixes(), validateReadableInputsBeforeRouting(), createReadableLayout() (+6 more)

### Community 27 - "check-render-output.mjs"
Cohesion: 0.07
Nodes (26): checks, collectLegendCollisions(), collectRelationshipCrossings(), composition, crossProduct(), ELEMENT_NUMERIC_ATTRS, HTML_VOID_ELEMENTS, htmlPath (+18 more)

### Community 28 - "row"
Cohesion: 0.07
Nodes (34): row(), at(), kind(), Architecture, Class, Dataflow, ERD, Lifecycle (+26 more)

### Community 29 - "render-tree.mjs"
Cohesion: 0.07
Nodes (29): all, ancestorsOf(), attachOf(), bandSize, bandStart, centerOf(), childrenOf, cliArgs (+21 more)

### Community 30 - "runtime.py"
Cohesion: 0.12
Nodes (12): classify(), _envelope(), failure(), hash_household(), run_blocking(), run_tool(), success(), api_nutrition() (+4 more)

### Community 31 - "register_tools"
Cohesion: 0.12
Nodes (30): 5. Idempotency Key Handling, 4. The 25-Phrase Golden Test Set, 9. MCP tool contracts, 1. Operating Principles & Standing Directives, 2. Product Overview, 3. Architecture & Tech Stack, 4. Current Phase & Progress Status, 4-Day Execution Schedule: (+22 more)

### Community 32 - "render.mjs"
Cohesion: 0.15
Nodes (20): layoutExplainerPanels(), finish(), css, dictionaries, escape(), icons, js, json() (+12 more)

### Community 33 - "YAYTP6L5.js"
Cohesion: 0.13
Nodes (37): E(), h(), I(), k(), L(), O(), P(), v() (+29 more)

### Community 34 - "func3"
Cohesion: 0.09
Nodes (38): func3(), validate27(), validate28(), validate30(), validate31(), validate33(), validate34(), validate36() (+30 more)

### Community 35 - "Ledger"
Cohesion: 0.12
Nodes (7): Ledger, body(), LedgerError, normalize_item(), normalize_unit(), parse_ts(), to_base()

### Community 36 - "validate.mjs"
Cohesion: 0.16
Nodes (22): escapeHtml(), inlineError(), parseInline(), problem(), segment(), referenceFor(), renderInline(), EDGE_KEYS (+14 more)

### Community 37 - "route-quality.mjs"
Cohesion: 0.12
Nodes (27): boundsForPoints(), boundsForRects(), cleanRouteDetourProblems(), collinearOverlap(), DEFAULTS, emptyControlPointClearance(), expandedRect(), inferredSide() (+19 more)

### Community 38 - "EEIX5ZYH.js"
Cohesion: 0.13
Nodes (26): addStyleData(), addSubsetData(), addTextData(), color(), Ct(), dt(), et(), getCurrentSets() (+18 more)

### Community 39 - "42UTT654.js"
Cohesion: 0.15
Nodes (25): addClass(), addPoint(), B(), ct(), Ht(), parse(), qt(), setAccDescription() (+17 more)

### Community 40 - "compileWorkflowInternal"
Cohesion: 0.12
Nodes (39): polylineBendContacts(), compileWorkflowInternal(), boundsOverlap(), candidateLabelRect(), compositionFrames(), corridorTopologyMatches(), finalizeReadableViewBox(), firstRouteNodeCollision() (+31 more)

### Community 41 - "IZOKQ2GT.js"
Cohesion: 0.22
Nodes (24): Kt(), f(), bt(), b(), ft(), gt(), j(), lt() (+16 more)

### Community 42 - "ref_node_url"
Cohesion: 0.12
Nodes (14): ajv, diagramTypes, __dirname, output, portableOutputWrappers, RESERVED_TYPE_NAMES, root, schemaIds (+6 more)

### Community 43 - "UPTXNAXN.js"
Cohesion: 0.15
Nodes (23): h(), l(), m(), p(), r(), Te(), Ke(), addLink() (+15 more)

### Community 44 - "workflow-v2.mjs"
Cohesion: 0.16
Nodes (30): clone(), diagnostic(), expandableViewBox(), legacyLayoutProbe(), legacyRequirementProbe(), migrateWorkflowDocument(), requiredViewBoxFrom(), result() (+22 more)

### Community 45 - "validateReadablePinnedGeometry"
Cohesion: 0.16
Nodes (28): authoredPinEvidence(), authoredRouteAssertionFields(), classifyFailedAutomaticCandidatePins(), combinations(), conflictPinsFromRemovalSets(), endpointSideIsHonored(), hasAbsoluteRoutePins(), hasAuthoredRouteAssertions() (+20 more)

### Community 46 - "diagrams.mjs"
Cohesion: 0.17
Nodes (22): attrs(), changesPreview(), compileExplainerDiagram(), decode(), duplicateCheck(), fail(), freezeBytes(), inferredId() (+14 more)

### Community 47 - "reader.js"
Cohesion: 0.14
Nodes (21): applyTheme(), cropDiagramPreviews(), ensureDiagramReadability(), exportImage(), fitDiagrams(), fitLaneFrames(), layoutBoard(), plan() (+13 more)

### Community 48 - "anchor"
Cohesion: 0.18
Nodes (31): anchor(), defaultFromSide(), defaultToSide(), joinRoutePoints(), automaticEndpointRepairs(), automaticForwardReversePx(), automaticPortCandidates(), clearStraightAutomaticPlan() (+23 more)

### Community 49 - "portable-path.mjs"
Cohesion: 0.29
Nodes (12): assertProfile(), classifySemanticCollision(), collisionError(), createSemanticIndex(), findSemanticCollision(), pathError(), PORTABLE_PATH_PROFILES, PortablePathError (+4 more)

### Community 50 - "parseExplainer"
Cohesion: 0.20
Nodes (21): csv(), parseExplainer(), addBlock(), assessment(), attributes(), boolean(), cells(), directive() (+13 more)

### Community 51 - "check.mjs"
Cohesion: 0.21
Nodes (9): checkExplainerHtml(), decode(), decodeURIComponentSafe(), isExplainerHtml(), scanHtml(), packPageBundle(), swap(), unpackPageBundle() (+1 more)

### Community 52 - "laneTop"
Cohesion: 0.22
Nodes (19): gapYBetween(), groupSpan(), measuredContentBounds(), phaseSpan(), renderGroup(), renderLane(), spanForCols(), workflowCompositionFrames() (+11 more)

### Community 53 - "test_ledger.py"
Cohesion: 0.19
Nodes (14): groceries(), led(), store(), test_concurrent_retries_apply_once(), test_concurrent_writes_from_many_connections(), test_event_log_is_append_only(), test_failed_op_rolls_back_whole_batch(), test_households_are_isolated() (+6 more)

### Community 54 - "diagnostics.mjs"
Cohesion: 0.24
Nodes (12): boundaryKey, fallbackDiagnostic(), formatDiagnostics(), installRendererDiagnosticBoundary(), normalizedDiagnostic(), plainObject(), readerSignal, recorded (+4 more)

### Community 55 - "config.py"
Cohesion: 0.17
Nodes (7): _bool(), ConfigError, _float(), _int(), _list(), check_household(), test_config_reads_platform_port()

### Community 56 - "PipeCdp"
Cohesion: 0.21
Nodes (5): browserEnvironment(), ChromeVisualBrowser, chromeVisualBrowserArgs(), evaluate(), PipeCdp

### Community 57 - "prepare.mjs"
Cohesion: 0.38
Nodes (13): embedded(), fail(), preparePanelPatch(), assertPreparedDependencies(), digest(), fail(), identity(), parseValidatedExplainer() (+5 more)

### Community 58 - "repository-evidence.mjs"
Cohesion: 0.25
Nodes (16): EVIDENCE_NODE_COLLECTIONS, evidenceFailure(), evidenceNodes(), gitValue(), hasRepositoryEvidence(), prefetchBlobs(), readBatchObjects(), runGit() (+8 more)

### Community 59 - "pathFor"
Cohesion: 0.27
Nodes (11): isReadableControlledRoute(), labelRectFor(), measuredPlanReceipt(), pathFor(), renderEdgeLabel(), renderEdgePath(), renderLegend(), roundedWorkflowPath() (+3 more)

### Community 60 - "EJ5KOXYD.js"
Cohesion: 0.25
Nodes (16): A(), b(), d(), E(), indent(), k(), L(), N() (+8 more)

### Community 61 - "parse_kitchen_utterance"
Cohesion: 0.15
Nodes (15): _extract_qty_and_unit(), _find_unit(), parse_kitchen_utterance(), ParsedItem, ParseResult, test_confirm_action_intents(), test_consume_action_detected(), test_explicit_quantities_parsed_accurately() (+7 more)

### Community 62 - "browser-check.mjs"
Cohesion: 0.26
Nodes (14): activate(), evaluate(), EXPLAINER_VIEWPORTS, explainerObservation(), explainerObservationDiagnostics(), expression(), inspectExplainerBrowser(), inspectNativePreviewLayout() (+6 more)

### Community 63 - "desktop-readability.mjs"
Cohesion: 0.14
Nodes (15): DECLARED_WIDE_READER_CONTRACT, DECLARED_WIDE_READER_MAX_WIDTH, DECLARED_WIDE_READER_RATIO, DECLARED_WIDE_REFERENCE_BODY_HORIZONTAL_PX, DECLARED_WIDE_REFERENCE_DIAGRAM_HORIZONTAL_PX, declaredWideReadabilityBudget(), describeFixedWidthOverflow(), DESKTOP_FIXED_VERTICAL_CHROME_PX (+7 more)

### Community 64 - "sources.mjs"
Cohesion: 0.37
Nodes (13): chartFromData(), deriveRepository(), digest(), fail(), gitBytes(), imageMime(), location(), readContained() (+5 more)

### Community 65 - "SousChefVoiceApp"
Cohesion: 0.16
Nodes (4): CookingMusicEngine, escapeHtml(), formatDisplayQty(), SousChefVoiceApp

### Community 66 - "parseAttrs"
Cohesion: 0.27
Nodes (14): collectArchitectureLeadingSpace(), collectLegendBoxes(), collectRelationshipLabelMasks(), collectSequenceColumnSpace(), collectSequenceNoteBorders(), collectUntransformedNodeRects(), legendTextWidth(), numberAttr() (+6 more)

### Community 67 - "scenarios.mjs"
Cohesion: 0.24
Nodes (10): detectGuideLanguage(), formatScenarioList(), listScenarioRecipes(), localized(), normalized(), publicGuideData(), RAW_RECIPES, recommendScenario() (+2 more)

### Community 68 - ""Sous-Chef": Voice-First Kitchen Inventory, Meal Planning & Nutrition Agent"
Cohesion: 0.08
Nodes (25): 0. Instructions for the AI assistant reading this document, 11. Recipe matching algorithm, 12. Nutrition, 13. AI / LLM strategy, 14. Security, privacy and compliance, 15. Observability and operations, 16.1 Tests, 16.2 Success metrics (+17 more)

### Community 69 - "collectArrows"
Cohesion: 0.22
Nodes (11): attrEntries(), collectArrows(), collectCompositionFrames(), collectNonFiniteAttrs(), continuousRoutePoints(), decodeNumericReferences(), inspectedPath(), isNumericAttr() (+3 more)

### Community 70 - "Authoring contract"
Cohesion: 0.12
Nodes (16): Authoring contract, Composition repair, Engineering profile default, Executable geometry rules, Explicit `via` coordinates, Hand-placed fallback, Label repair, Language consistency (+8 more)

### Community 71 - "render-explainer.mjs"
Cohesion: 0.22
Nodes (7): bytes, candidate, capture, inputPath, { outputPath }, request, sourceText

### Community 72 - "authoring-contract.md"
Cohesion: 0.20
Nodes (3): Bundled Viewer catalogs, Agent decision path, Brand marks

### Community 73 - "validatePortablePath"
Cohesion: 0.18
Nodes (24): Compact native diagrams, architecture(), classDiagram(), dataflow(), erd(), explainer(), lifecycle(), sequence() (+16 more)

### Community 74 - "open-artifact.mjs"
Cohesion: 0.24
Nodes (10): childPath, normalize(), startDeliveryUpdateCheck(), unavailable(), failureDetails(), launchTarget(), launchTimeout(), openArtifact() (+2 more)

### Community 75 - "analyzeSvgPath"
Cohesion: 0.53
Nodes (4): analyzeSvgPath(), ARITY, failure(), tokenize()

### Community 76 - "charts.mjs"
Cohesion: 0.18
Nodes (3): compileExplainerChart(), NATIVE, pieLegend()

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
Cohesion: 0.20
Nodes (9): ordinaryRouter(), sideFor(), Cardinality ink, Domain bands, Entity-Relationship Renderer, Layout and routing, Reading a schema, The legend band (+1 more)

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

### Community 90 - "parseExplainerDiff"
Cohesion: 0.46
Nodes (7): fileName(), parseExplainerDiff(), fail(), finishHunk(), startFile(), sourceLines(), containsExplainerSecret()

### Community 91 - "Lifecycle Renderer"
Cohesion: 0.29
Nodes (8): icon(), Node icons, Design rules, Input, Layout, Legend and state marks, Lifecycle Renderer, Validation

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

### Community 100 - "captureRemoteBrand"
Cohesion: 0.40
Nodes (6): captureRemoteBrand(), imageData(), readHtmlHeadLinks(), readLimited(), remoteBrand(), validIcoImageRanges()

### Community 101 - "engineering-profiles.mjs"
Cohesion: 0.47
Nodes (5): DEPLOYMENT_BOUNDARY_KINDS, deploymentOwnershipDiagnostics(), membership(), PRIVATE_STATE_TYPES, subject()

### Community 102 - "Hierarchy and Tree Renderer"
Cohesion: 0.33
Nodes (6): Expand and collapse, Hierarchy and Tree Renderer, Input, Layout, Structure checks, Tested size

### Community 103 - "Reliability & Golden Set Testing Engineering Standard"
Cohesion: 0.33
Nodes (5): 1. Testing Philosophy (Reliability #1), 2. Pytest Fixture Architecture (`tests/conftest.py`), 3. Synthetic DB Outage & Timeout Test, 5. Implementation Checklist, Reliability & Golden Set Testing Engineering Standard

### Community 104 - "4. Conversation design"
Cohesion: 0.33
Nodes (6): 4.1 Channels, 4.2 Persona and voice rules, 4.3 Key flows, 4.4 Failure flows, 4.5 Proactive behavior, 4. Conversation design

### Community 105 - "Authoring defaults"
Cohesion: 0.40
Nodes (5): Authoring defaults, Composition and meaning, Evidence and schema, Layout and routing, Presentation and modes

### Community 106 - "validateSchema"
Cohesion: 0.90
Nodes (4): annotatedPath(), annotatePath(), formatErrors(), validateSchema()

### Community 107 - "5. Functional requirements"
Cohesion: 0.40
Nodes (5): 5. Functional requirements, Cooking and nutrition, Inventory, Platform, Recipes

### Community 108 - "Architecture layout repair"
Cohesion: 0.50
Nodes (4): Architecture layout repair, Choose the repair scope, One coherent repair, directCorridorBlockers()

### Community 109 - "Execution Waterfall Renderer"
Cohesion: 0.50
Nodes (3): Execution Waterfall Renderer, Layout, Tested size

### Community 111 - "7. Architecture"
Cohesion: 0.50
Nodes (4): 7.1 Components, 7.2 Key design choices, 7.3 Model gateway (R3), 7. Architecture

## Knowledge Gaps
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `success()` connect `runtime.py` to `Lifecycle Renderer`, `row`, `test_server.py`?**
  _High betweenness centrality (0.108) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `compileWorkflowInternal()` (e.g. with `acceptsFix()` and `compareCost()`) actually correct?**
  _`compileWorkflowInternal()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Should `archify.mjs` be split into smaller, more focused modules?**
  _Cohesion score 0.052355396541443056 - nodes in this community are weakly interconnected._
- **Why does `icon()` connect `Lifecycle Renderer` to `render.mjs`, `validatePortablePath`?**
  _High betweenness centrality (0.085) - this node is a cross-community bridge._
- **Should `check-update.mjs` be split into smaller, more focused modules?**
  _Cohesion score 0.05570291777188329 - nodes in this community are weakly interconnected._
- **Why does `Legend and state marks` connect `Lifecycle Renderer` to `runtime.py`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Should `render-erd.mjs` be split into smaller, more focused modules?**
  _Cohesion score 0.04298245614035088 - nodes in this community are weakly interconnected._