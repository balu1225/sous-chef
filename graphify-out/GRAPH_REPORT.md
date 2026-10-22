# Graph Report - alexavoiceassistant  (2026-10-21)

## Corpus Check
- 214 files · ~1,398,286 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .css 2, .example 1)

## Summary
- 3162 nodes · 9151 edges · 132 communities (126 shown, 6 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 404 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `bd6bfde6`
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
- package.json
- render-timeline.mjs
- atomic-output.mjs
- createRouter
- build_app
- finalize.mjs
- L4LY553T.js
- brand-marks.mjs
- preview.mjs
- build
- check-render-output.mjs
- row
- render-tree.mjs
- server.py
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
- anchor
- UPTXNAXN.js
- workflow-v2.mjs
- formatDuration
- diagrams.mjs
- reader.js
- commandDeliver
- portable-path.mjs
- validateReadablePinnedGeometry
- page-bundle.mjs
- workflow-compiler.mjs
- test_ledger.py
- laneTop
- config.py
- PipeCdp
- prepare.mjs
- repository-evidence.mjs
- commandMigrate
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
- commandValidate
- Hierarchy and Tree Renderer
- open-artifact.mjs
- 4. Conversation design
- Authoring defaults
- scripts
- 5. Functional requirements
- pathFor
- detail
- generate-brand-marks.mjs
- 7. Architecture
- context_tracker.md
- brand-marks/README.md
- pele/README.md
- update-awareness.md
- Sous-Chef: Master Project Context & Living Log
- erd/grid.mjs
- generate-validators.mjs
- parseInline
- Lifecycle Renderer
- validateExplainer
- cardinalityOf
- parseExplainerDiff
- Data Flow Renderer
- renderRelationshipLabel
- renderEntityColumnRows
- Reliability & Golden Set Testing Engineering Standard
- placed
- domainGroups
- recordedEnd
- start_tunnel.sh

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
- `Execution Steps:` --references--> `query_inventory()`  [INFERRED]
  PROJECT_CONTEXT.md → src/sous_chef/server.py
- `Goal` --references--> `query_inventory()`  [INFERRED]
  PROJECT_CONTEXT.md → src/sous_chef/server.py

## Import Cycles
- None detected.

## Communities (132 total, 6 thin omitted)

### Community 0 - "archify.mjs"
Cohesion: 0.07
Nodes (49): captureOwnedStagingFile(), CHECK_FIXES, cleanupOwnedStagingDirectory(), [command, ...args], COMMAND_USAGE, commandBrands(), commandBrowserCheck(), commandBrowserEvidence() (+41 more)

### Community 1 - "check-update.mjs"
Cohesion: 0.06
Nodes (111): acquireOperation(), assertBoundedRegularFile(), assertCacheTargetAbsent(), assertRenameableCacheEntry(), assertSafeCacheEntry(), assertSafeDirectory(), assertSafeRegularFile(), cacheMkdir() (+103 more)

### Community 2 - "render-erd.mjs"
Cohesion: 0.06
Nodes (35): bandKey(), channelFallback(), cliArgs, corridorKey(), { diagram: er, template, outPath, sourceEvidence }, __dirname, DOMAIN_HUES, domainBandBox() (+27 more)

### Community 3 - "generated-validators.mjs"
Cohesion: 0.03
Nodes (73): pattern10, pattern11, pattern12, pattern13, pattern133, pattern14, pattern15, pattern16 (+65 more)

### Community 4 - "geometry.mjs"
Cohesion: 0.09
Nodes (66): validateArchitecture(), validateClassDiagram(), validateDataflow(), validateEr(), validateSequence(), recordDiagnostic(), throwDiagnosticProblems(), anchorFitsCanvas() (+58 more)

### Community 5 - "cli.mjs"
Cohesion: 0.06
Nodes (49): defaultDeliveryPaths(), __dirname, bytes, candidate, capture, inputPath, { outputPath }, request (+41 more)

### Community 6 - "architecture-delta.mjs"
Cohesion: 0.07
Nodes (66): addNodeMarker(), addState(), annotateArchitectureSideSvg(), architectureDeltaChangeRows(), ArchitectureDeltaError, BOUNDARY_FIELDS, boundaryChangeMap(), boundaryElements() (+58 more)

### Community 7 - "render-class.mjs"
Cohesion: 0.04
Nodes (81): hasAutomaticRouteGeometry(), renderConnectionPath(), attributeText(), autoViewBox(), bands, busGroups, busPaths, cliArgs (+73 more)

### Community 8 - "visual-check.mjs"
Cohesion: 0.08
Nodes (58): appendEvidenceCleanupWarning(), appendEvidencePublicationFailure(), baseReceipt(), beginVisualEvidenceWrite(), CAPTURE_VIEWPORTS, CHROME_NO_SANDBOX_ENV, CHROME_STARTUP_TIMEOUT_MS, cleanupStagedEvidence() (+50 more)

### Community 9 - "path-semantics.mjs"
Cohesion: 0.11
Nodes (52): visualEvidenceOwnershipMatches(), nativeOutputDiagnostic(), rejectWindowsIpcShare(), resolveNativeOutputDirectory(), throwNativeOutputDiagnostic(), validateNativeOutputPath(), validateWindowsNativeComponent(), validateWindowsRawUncRoot() (+44 more)

### Community 10 - "render-architecture.mjs"
Cohesion: 0.06
Nodes (47): DEFAULT_GRID, gridLayout(), resolveComponentPos(), validateGridPlacement(), architectureLegendEntries, autoViewBoxFor(), boundaryLabelWidth(), buildLayoutReport() (+39 more)

### Community 11 - "render-lifecycle.mjs"
Cohesion: 0.06
Nodes (54): assignArcLevels(), assignTracks(), bracketOf, brackets, bracketTargets, canvasWidth, countCrossings(), depth (+46 more)

### Community 12 - "i18n.mjs"
Cohesion: 0.12
Nodes (28): applyLocaleTranslations(), BUNDLED_CATALOGS, bundledCatalog(), bundledLocaleFor(), CANONICAL_KEYS, CANONICAL_PLACEHOLDERS, catalogFor(), classifyTranslations() (+20 more)

### Community 13 - "workflow-compiler.mjs"
Cohesion: 0.05
Nodes (83): boundaryRect(), ensureAutoLegendFits(), renderLegend(), autoViewBox(), preferredWidth(), validateStructure(), arrowClass, automaticCanvasWidth() (+75 more)

### Community 14 - "UKSIWDDN.js"
Cohesion: 0.10
Nodes (38): D(), expect(), fail(), H(), j(), S(), take(), text() (+30 more)

### Community 15 - "test_server.py"
Cohesion: 0.07
Nodes (39): ERD, Schema lookup, Input, Legend presentation contract, call(), db(), _free_port(), init_only() (+31 more)

### Community 16 - "render-waterfall.mjs"
Cohesion: 0.05
Nodes (35): buildLayoutReport(), byId, children, cliArgs, details, { diagram: wf, template, outPath, sourceEvidence }, __dirname, footprint (+27 more)

### Community 17 - "package.json"
Cohesion: 0.11
Nodes (17): bin, archify, description, devDependencies, ajv, simple-icons, engines, node (+9 more)

### Community 18 - "render-timeline.mjs"
Cohesion: 0.05
Nodes (95): componentContext(), renderBoundaryFrame(), renderBoundaryLabel(), renderComponent(), renderConnectionLabel(), renderSvg(), renderSvg(), renderType() (+87 more)

### Community 19 - "atomic-output.mjs"
Cohesion: 0.14
Nodes (47): captureOwnedDeliverySidecars(), args, backupOwnedPublishedEntry(), backupPublicRegularFileBinding(), captureAtomicOutput(), captureRegularFileBinding(), captureRegularFileHandle(), captureRequestedEntry() (+39 more)

### Community 20 - "createRouter"
Cohesion: 0.14
Nodes (44): createRouter(), alignFacingPorts(), automaticEndpoint(), cachePath(), candidateSidePairs(), collinearBacktrack(), collinearOverlapLength(), computePath() (+36 more)

### Community 21 - "build_app"
Cohesion: 0.07
Nodes (21): Store, execute_cooking_deduction(), find_recipe_by_id(), get_all_recipes(), _load_seeds(), match_recipes(), calculate_item_macros(), calculate_meal_nutrition() (+13 more)

### Community 22 - "finalize.mjs"
Cohesion: 0.10
Nodes (42): allChecksPassed(), browserEvidence(), captureReceipt(), compactFinalizeReceipt(), consolidateDiagnostics(), defaultFinalizeReceiptPath(), defaultFinalizeSummaryPath(), defaultRunner() (+34 more)

### Community 23 - "L4LY553T.js"
Cohesion: 0.11
Nodes (33): mt(), e(), o(), r(), t(), u(), x(), addPlot() (+25 more)

### Community 24 - "brand-marks.mjs"
Cohesion: 0.11
Nodes (19): BASIC_HTML_REFERENCES, beforeDeadline(), checkedFetch(), COLLECTIONS, decodeIconHref(), HTML_C1_REFERENCES, iconCandidates(), ipv4Private() (+11 more)

### Community 25 - "preview.mjs"
Cohesion: 0.13
Nodes (33): atomicOutputError(), atomicOutputFailure(), captureOwnedDirectory(), cleanupOwnedDirectory(), cliPath, compactMessage(), diagramTypes, here (+25 more)

### Community 26 - "build"
Cohesion: 0.10
Nodes (61): busRouteConflict(), compileDataflow(), attempt(), build(), compactCorridors(), crossingFlows(), detourFor(), endpointStubs() (+53 more)

### Community 27 - "check-render-output.mjs"
Cohesion: 0.07
Nodes (25): attrEntries(), checks, collectLegendCollisions(), collectNonFiniteAttrs(), collectRelationshipCrossings(), composition, crossProduct(), decodeNumericReferences() (+17 more)

### Community 28 - "row"
Cohesion: 0.11
Nodes (23): row(), at(), kind(), Architecture, Class, Dataflow, Lifecycle, Mode placement (+15 more)

### Community 29 - "render-tree.mjs"
Cohesion: 0.05
Nodes (40): nodeTextFit, SEMANTIC_SIGIL_FOOTPRINT, SEMANTIC_SIGIL_INSET, SEMANTIC_SIGIL_SIZE, serializeScriptJson(), SIGIL_SHAPE, SIGIL_TONE, SOURCE_BADGE_FOOTPRINT (+32 more)

### Community 30 - "server.py"
Cohesion: 0.06
Nodes (15): fallback_tag_ingredients(), is_bedrock_configured(), tag_recipe_ingredients(), _envelope(), failure(), hash_household(), run_blocking(), setup_logging() (+7 more)

### Community 31 - "register_tools"
Cohesion: 0.17
Nodes (25): 5. Idempotency Key Handling, 4. The 25-Phrase Golden Test Set, 9. MCP tool contracts, 4-Day Execution Schedule:, 5. Scope Selection: Option A (Demo-Critical), 9. Change & Activity History, In Scope for Option A:, classify() (+17 more)

### Community 32 - "render.mjs"
Cohesion: 0.14
Nodes (22): compileExplainerChart(), pieLegend(), layoutExplainerPanels(), finish(), css, dictionaries, escape(), icons (+14 more)

### Community 33 - "YAYTP6L5.js"
Cohesion: 0.14
Nodes (31): Ge(), I(), Z(), ae(), be(), Ct(), de(), $e() (+23 more)

### Community 34 - "func3"
Cohesion: 0.09
Nodes (38): func3(), validate27(), validate28(), validate30(), validate31(), validate33(), validate34(), validate36() (+30 more)

### Community 35 - "Ledger"
Cohesion: 0.10
Nodes (8): 6. Non-functional requirements, Ledger, body(), LedgerError, normalize_item(), normalize_unit(), parse_ts(), to_base()

### Community 36 - "validate.mjs"
Cohesion: 0.31
Nodes (7): EDGE_KEYS, NODE_KEYS, READER_IDS, lintExplainerWriting(), proseMask(), RULES, sentences()

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
Cohesion: 0.10
Nodes (49): compileWorkflowInternal(), automaticForwardReversePx(), boundsOverlap(), candidateLabelRect(), compositionFrames(), corridorTopologyMatches(), firstRouteNodeCollision(), isReadableAutomaticRoute() (+41 more)

### Community 41 - "IZOKQ2GT.js"
Cohesion: 0.24
Nodes (19): $t(), f(), bt(), b(), ft(), gt(), j(), lt() (+11 more)

### Community 42 - "anchor"
Cohesion: 0.18
Nodes (31): anchor(), defaultFromSide(), defaultToSide(), joinRoutePoints(), automaticEndpointRepairs(), automaticPortCandidates(), clearStraightAutomaticPlan(), compareCost() (+23 more)

### Community 43 - "UPTXNAXN.js"
Cohesion: 0.17
Nodes (21): l(), m(), p(), i(), addLink(), be(), de(), $e() (+13 more)

### Community 44 - "workflow-v2.mjs"
Cohesion: 0.11
Nodes (36): clone(), diagnostic(), expandableViewBox(), legacyLayoutProbe(), legacyRequirementProbe(), migrateWorkflowDocument(), requiredViewBoxFrom(), result() (+28 more)

### Community 45 - "formatDuration"
Cohesion: 0.50
Nodes (4): axisLabels, formatDuration(), number(), timeNumber()

### Community 46 - "diagrams.mjs"
Cohesion: 0.09
Nodes (47): attrs(), changesPreview(), compileExplainerDiagram(), decode(), duplicateCheck(), fail(), freezeBytes(), inferredId() (+39 more)

### Community 47 - "reader.js"
Cohesion: 0.14
Nodes (21): applyTheme(), cropDiagramPreviews(), ensureDiagramReadability(), exportImage(), fitDiagrams(), fitLaneFrames(), layoutBoard(), plan() (+13 more)

### Community 48 - "commandDeliver"
Cohesion: 0.16
Nodes (30): acquireDeliveryLock(), artifactIdentity(), assertDeliveryOwnership(), assertOwnedDeliveryLock(), beginDeliveryAttempt(), canonicalExistingDeliveryOutput(), captureDeliveryTargetState(), commandDeliver() (+22 more)

### Community 49 - "portable-path.mjs"
Cohesion: 0.29
Nodes (12): assertProfile(), classifySemanticCollision(), collisionError(), createSemanticIndex(), findSemanticCollision(), pathError(), PORTABLE_PATH_PROFILES, PortablePathError (+4 more)

### Community 50 - "validateReadablePinnedGeometry"
Cohesion: 0.16
Nodes (28): authoredPinEvidence(), authoredRouteAssertionFields(), classifyFailedAutomaticCandidatePins(), combinations(), conflictPinsFromRemovalSets(), endpointSideIsHonored(), hasAbsoluteRoutePins(), hasAuthoredRouteAssertions() (+20 more)

### Community 51 - "page-bundle.mjs"
Cohesion: 0.60
Nodes (3): packPageBundle(), swap(), unpackPageBundle()

### Community 52 - "workflow-compiler.mjs"
Cohesion: 0.10
Nodes (32): predictedFixedWidthOverflow(), componentFill, componentText, NODE_CARD_ATTR, nodeCardStyle(), TONES, authoredNodeHeight(), authoredNodeWidth() (+24 more)

### Community 53 - "test_ledger.py"
Cohesion: 0.19
Nodes (14): groceries(), led(), store(), test_concurrent_retries_apply_once(), test_concurrent_writes_from_many_connections(), test_event_log_is_append_only(), test_failed_op_rolls_back_whole_batch(), test_households_are_isolated() (+6 more)

### Community 54 - "laneTop"
Cohesion: 0.19
Nodes (21): variantAccent(), groupSpan(), measuredContentBounds(), phaseSpan(), renderGroup(), renderLane(), renderPhase(), renderSvg() (+13 more)

### Community 55 - "config.py"
Cohesion: 0.14
Nodes (11): _bool(), Config, ConfigError, _float(), _int(), _list(), check_household(), main() (+3 more)

### Community 56 - "PipeCdp"
Cohesion: 0.21
Nodes (5): browserEnvironment(), ChromeVisualBrowser, chromeVisualBrowserArgs(), evaluate(), PipeCdp

### Community 57 - "prepare.mjs"
Cohesion: 0.29
Nodes (14): embedded(), fail(), preparePanelPatch(), assertPreparedDependencies(), digest(), fail(), identity(), parseValidatedExplainer() (+6 more)

### Community 58 - "repository-evidence.mjs"
Cohesion: 0.25
Nodes (16): EVIDENCE_NODE_COLLECTIONS, evidenceFailure(), evidenceNodes(), gitValue(), hasRepositoryEvidence(), prefetchBlobs(), readBatchObjects(), runGit() (+8 more)

### Community 59 - "commandMigrate"
Cohesion: 0.18
Nodes (21): artifactCheckMaxBuffer(), checkerDiagnostics(), checkerOutputLimitDiagnostics(), commandCheck(), commandMigrate(), compositionFixes(), deliveryCommitRecoveryDiagnostic(), deliveryTargetStateDiagnostic() (+13 more)

### Community 60 - "EJ5KOXYD.js"
Cohesion: 0.28
Nodes (15): A(), b(), d(), E(), indent(), k(), L(), N() (+7 more)

### Community 61 - "parse_kitchen_utterance"
Cohesion: 0.10
Nodes (20): _extract_qty_and_unit(), _find_unit(), parse_kitchen_utterance(), ParsedItem, ParseResult, get_remedy_for_mishap(), KitchenMishap, handler() (+12 more)

### Community 62 - "browser-check.mjs"
Cohesion: 0.17
Nodes (19): activate(), evaluate(), EXPLAINER_VIEWPORTS, explainerObservation(), explainerObservationDiagnostics(), expression(), inspectExplainerBrowser(), inspectNativePreviewLayout() (+11 more)

### Community 63 - "desktop-readability.mjs"
Cohesion: 0.14
Nodes (15): DECLARED_WIDE_READER_CONTRACT, DECLARED_WIDE_READER_MAX_WIDTH, DECLARED_WIDE_READER_RATIO, DECLARED_WIDE_REFERENCE_BODY_HORIZONTAL_PX, DECLARED_WIDE_REFERENCE_DIAGRAM_HORIZONTAL_PX, declaredWideReadabilityBudget(), describeFixedWidthOverflow(), DESKTOP_FIXED_VERTICAL_CHROME_PX (+7 more)

### Community 64 - "sources.mjs"
Cohesion: 0.34
Nodes (14): chartFromData(), containsExplainerSecret(), deriveRepository(), digest(), fail(), gitBytes(), imageMime(), location() (+6 more)

### Community 65 - "SousChefVoiceApp"
Cohesion: 0.15
Nodes (4): CookingMusicEngine, escapeHtml(), formatDisplayQty(), SousChefVoiceApp

### Community 66 - "parseAttrs"
Cohesion: 0.29
Nodes (14): collectArchitectureLeadingSpace(), collectCompositionFrames(), collectLegendBoxes(), collectRelationshipLabelMasks(), collectSequenceColumnSpace(), collectSequenceNoteBorders(), collectUntransformedNodeRects(), legendTextWidth() (+6 more)

### Community 67 - "scenarios.mjs"
Cohesion: 0.24
Nodes (10): detectGuideLanguage(), formatScenarioList(), listScenarioRecipes(), localized(), normalized(), publicGuideData(), RAW_RECIPES, recommendScenario() (+2 more)

### Community 68 - ""Sous-Chef": Voice-First Kitchen Inventory, Meal Planning & Nutrition Agent"
Cohesion: 0.08
Nodes (24): 0. Instructions for the AI assistant reading this document, 11. Recipe matching algorithm, 12. Nutrition, 13. AI / LLM strategy, 14. Security, privacy and compliance, 15. Observability and operations, 16.1 Tests, 16.2 Success metrics (+16 more)

### Community 69 - "collectArrows"
Cohesion: 0.40
Nodes (6): collectArrows(), continuousRoutePoints(), inspectedPath(), isPoint(), lineSegments(), parseRoutePoints()

### Community 70 - "Authoring contract"
Cohesion: 0.12
Nodes (16): Authoring contract, Composition repair, Engineering profile default, Executable geometry rules, Explicit `via` coordinates, Hand-placed fallback, Label repair, Language consistency (+8 more)

### Community 71 - "ref_node_fs"
Cohesion: 0.39
Nodes (5): createOwnedTempDirectory(), remove(), directoryIdentity(), retryable, verifyIdentity()

### Community 72 - "authoring-contract.md"
Cohesion: 0.22
Nodes (3): Bundled Viewer catalogs, Agent decision path, Brand marks

### Community 73 - "validatePortablePath"
Cohesion: 0.18
Nodes (23): Compact native diagrams, architecture(), classDiagram(), dataflow(), erd(), explainer(), lifecycle(), sequence() (+15 more)

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

### Community 101 - "commandValidate"
Cohesion: 0.25
Nodes (21): commandDemo(), commandExamples(), commandFinalize(), commandPatch(), commandPreview(), commandRender(), commandValidate(), exitFrom() (+13 more)

### Community 102 - "Hierarchy and Tree Renderer"
Cohesion: 0.29
Nodes (6): Expand and collapse, Hierarchy and Tree Renderer, Input, Layout, Structure checks, Tested size

### Community 103 - "open-artifact.mjs"
Cohesion: 0.16
Nodes (14): childPath, normalize(), startDeliveryUpdateCheck(), unavailable(), failureDetails(), launchTarget(), launchTimeout(), openArtifact() (+6 more)

### Community 104 - "4. Conversation design"
Cohesion: 0.33
Nodes (6): 4.1 Channels, 4.2 Persona and voice rules, 4.3 Key flows, 4.4 Failure flows, 4.5 Proactive behavior, 4. Conversation design

### Community 105 - "Authoring defaults"
Cohesion: 0.40
Nodes (5): Authoring defaults, Composition and meaning, Evidence and schema, Layout and routing, Presentation and modes

### Community 106 - "scripts"
Cohesion: 0.12
Nodes (16): scripts, build:gallery, build:guide, build:readme-showcase, build:start, check:brand-marks, check:release-identity, check:validators (+8 more)

### Community 107 - "5. Functional requirements"
Cohesion: 0.40
Nodes (5): 5. Functional requirements, Cooking and nutrition, Inventory, Platform, Recipes

### Community 108 - "pathFor"
Cohesion: 0.24
Nodes (14): pathFor(), buildLayoutReport(), bundledRelationshipD(), bundledTrunkPaths(), legendLayout(), markerStyleOf(), relationshipAutoRouted(), relationshipStrokeWidth() (+6 more)

### Community 109 - "detail"
Cohesion: 0.50
Nodes (3): Execution Waterfall Renderer, Layout, Tested size

### Community 110 - "generate-brand-marks.mjs"
Cohesion: 0.18
Nodes (13): catalog, catalogPath, domains, fail(), generated, here, ids, lookupForms() (+5 more)

### Community 111 - "7. Architecture"
Cohesion: 0.50
Nodes (4): 7.1 Components, 7.2 Key design choices, 7.3 Model gateway (R3), 7. Architecture

### Community 116 - "Sous-Chef: Master Project Context & Living Log"
Cohesion: 0.15
Nodes (12): 1. Operating Principles & Standing Directives, 2. Product Overview, 3. Architecture & Tech Stack, 4. Current Phase & Progress Status, 6. P1 Step 2: Connect to Alexa+ (Detailed Plan), 7. Decision Log, 8. Friction Log, Execution Steps: (+4 more)

### Community 117 - "erd/grid.mjs"
Cohesion: 0.26
Nodes (11): bandedLayout(), DEFAULT_ER_GRID, entityHeight(), erGridLayout(), gridColumn(), resolvedEntityWidth(), resolveEntityPos(), validateErGridPlacement() (+3 more)

### Community 118 - "generate-validators.mjs"
Cohesion: 0.18
Nodes (10): ajv, diagramTypes, __dirname, output, portableOutputWrappers, RESERVED_TYPE_NAMES, root, schemaIds (+2 more)

### Community 119 - "parseInline"
Cohesion: 0.43
Nodes (7): escapeHtml(), inlineError(), parseInline(), problem(), segment(), referenceFor(), renderInline()

### Community 120 - "Lifecycle Renderer"
Cohesion: 0.29
Nodes (8): icon(), Node icons, Design rules, Input, Layout, Legend and state marks, Lifecycle Renderer, Validation

### Community 121 - "validateExplainer"
Cohesion: 0.64
Nodes (8): validateExplainer(), diagramTarget(), fail(), id(), location(), reference(), references(), text()

### Community 122 - "cardinalityOf"
Cohesion: 0.32
Nodes (8): cardinalityGlyphParts(), cardinalityMarkerId(), cardinalityMarkerMarkup(), cardinalityOf(), legendSwatch(), optionalOf(), relationshipEnds(), renderCardinalityDefs()

### Community 123 - "parseExplainerDiff"
Cohesion: 0.52
Nodes (6): fileName(), parseExplainerDiff(), fail(), finishHunk(), startFile(), sourceLines()

### Community 124 - "Data Flow Renderer"
Cohesion: 0.33
Nodes (5): Data Flow Renderer, Design Rules, Input, Layout budget, Legend

### Community 125 - "renderRelationshipLabel"
Cohesion: 0.40
Nodes (6): defaultErLabelPoint(), erLabelPoint(), labelColumnGaps(), relationshipLabelBox(), relationshipLabelWidth(), renderRelationshipLabel()

### Community 126 - "renderEntityColumnRows"
Cohesion: 0.47
Nodes (6): keyColumnWidth(), keyGlyphWidth(), keyRoles(), renderEntityColumnRows(), renderKeyBadge(), renderKeyGlyphs()

### Community 127 - "Reliability & Golden Set Testing Engineering Standard"
Cohesion: 0.33
Nodes (5): 1. Testing Philosophy (Reliability #1), 2. Pytest Fixture Architecture (`tests/conftest.py`), 3. Synthetic DB Outage & Timeout Test, 5. Implementation Checklist, Reliability & Golden Set Testing Engineering Standard

### Community 128 - "placed"
Cohesion: 0.40
Nodes (5): placed, serviceLegendEntries, serviceTone(), toneOf(), xOf()

### Community 129 - "domainGroups"
Cohesion: 0.50
Nodes (4): domainGroups, gridRunIsContiguous(), placedByGrid(), unlabelableDomains

### Community 130 - "recordedEnd"
Cohesion: 0.67
Nodes (3): recordedEnd(), spans, t1

## Knowledge Gaps
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `success()` connect `server.py` to `Lifecycle Renderer`, `row`, `register_tools`, `test_server.py`?**
  _High betweenness centrality (0.130) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `compileWorkflowInternal()` (e.g. with `acceptsFix()` and `compareCost()`) actually correct?**
  _`compileWorkflowInternal()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Should `archify.mjs` be split into smaller, more focused modules?**
  _Cohesion score 0.07183673469387755 - nodes in this community are weakly interconnected._
- **Why does `icon()` connect `Lifecycle Renderer` to `render.mjs`, `validatePortablePath`?**
  _High betweenness centrality (0.100) - this node is a cross-community bridge._
- **Should `check-update.mjs` be split into smaller, more focused modules?**
  _Cohesion score 0.05570291777188329 - nodes in this community are weakly interconnected._
- **Why does `Legend and state marks` connect `Lifecycle Renderer` to `server.py`?**
  _High betweenness centrality (0.095) - this node is a cross-community bridge._
- **Should `render-erd.mjs` be split into smaller, more focused modules?**
  _Cohesion score 0.06258890469416785 - nodes in this community are weakly interconnected._