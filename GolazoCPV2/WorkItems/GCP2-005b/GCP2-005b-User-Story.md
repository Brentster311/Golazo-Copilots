# GCP2-005b: Shared React WebView

**Status**: BACKLOG  
**Priority**: Low  
**Size**: M  
**Created**: 2026-01-27  
**Parent**: GCP2-005

---

## User Story

- **Title**: Shared React WebView
- **As a**: Golazo extension developer
- **I want**: A shared React UI for the workflow panel
- **So that**: VS Code and Visual Studio have identical, maintainable UIs

- **Out of scope**:
  - VS Code extension shell (GCP2-005a)
  - Visual Studio extension shell (GCP2-005c)
  - Agent/protocol (GCP2-001)

- **Assumptions**:
  - **Assumption (explicit)**: React + TypeScript with Vite bundler
  - **Assumption (explicit)**: CSS variables for theme adaptation
  - **Assumption (explicit)**: postMessage API for host communication

- **Acceptance Criteria**:
  - [ ] React components: Header, PhaseIndicator, RoleList, Checklist, WorkItemSwitcher
  - [ ] Adapts to VS Code and Visual Studio themes via CSS variables
  - [ ] postMessage API for communication with host extension
  - [ ] Single HTML+JS+CSS bundle output (< 500KB)
  - [ ] Handles loading, error, and connected states
  - [ ] Responsive to panel width
  - [ ] Source maps included for debugging

- **Non-functional requirements**:
  - Bundle size < 500KB
  - Initial render < 200ms
  - No external runtime dependencies (all bundled)

- **Telemetry / metrics expected**:
  - None for MVP

- **Rollout / rollback notes**:
  - Built artifact consumed by GCP2-005a and GCP2-005c

---

## Component Hierarchy

```
<GolazoPanel>
  <Header workItem={...} />
  <PhaseIndicator phase="development" />
  <RoleList roles={...} currentRole="developer" />
  <Checklist title="DoR" items={...} />
  <Checklist title="DoD" items={...} />
  <WorkItemSwitcher items={...} onSwitch={...} />
</GolazoPanel>
```

---

## Dependencies

- GCP2-003 (State schema for type definitions)
7. [ ] Deviation/audit trail viewer

### Styling
8. [ ] Adapts to VS Code themes (light/dark)
9. [ ] Adapts to Visual Studio themes
10. [ ] Uses CSS variables for theming
11. [ ] Responsive to panel width

### Communication
12. [ ] `postMessage` API for host communication
13. [ ] Receives state updates from host
14. [ ] Sends user actions to host (switch, create, etc.)
15. [ ] Handles connection state (loading, error, connected)

### Build
16. [ ] Single HTML+JS+CSS bundle output
17. [ ] No external dependencies at runtime
18. [ ] Bundle size < 500KB
19. [ ] Source maps for debugging

## Component Hierarchy

```
<GolazoPanel>
  <Header workItem={...} />
  <PhaseIndicator phase="development" />
  <RoleList roles={...} currentRole="developer" />
  <Checklist title="DoR" items={...} />
  <Checklist title="DoD" items={...} />
  <WorkItemSwitcher items={...} onSwitch={...} />
  <DeviationList deviations={...} />
</GolazoPanel>
```

## UI Mockup

```
???????????????????????????????????
? ?? GCP2-005b                    ?
? Shared React WebView            ?
? Profile: Complete               ?
???????????????????????????????????
? ??????????????? Development    ?
???????????????????????????????????
? ROLES                           ?
? ? Project Owner                 ?
? ? Program Manager               ?
? ? Tester                        ?
? ? Architect                     ?
? ? Developer         ? current   ?
? ? Refactor Expert               ?
? ? Builder                       ?
? ? Documentor                    ?
???????????????????????????????????
? DEFINITION OF READY        ?    ?
? ? User Story exists             ?
? ? Scope bounded                 ?
? ? Test cases documented         ?
? ? Design approved               ?
???????????????????????????????????
? DEFINITION OF DONE        3/7   ?
? ? Branch created                ?
? ? Tests written first           ?
? ? Tests pass                    ?
? ? Build passes                  ?
? ? Refactor complete             ?
? ? Docs updated                  ?
? ? Committed                     ?
???????????????????????????????????
? [Switch: GCP2-005b ?]           ?
???????????????????????????????????
```

## Message Protocol (Host ? WebView)

### Host ? WebView
```typescript
// State update
{ type: 'state', payload: GolazoState }

// Theme change
{ type: 'theme', payload: { dark: boolean, colors: {...} } }

// Work item list
{ type: 'workItems', payload: WorkItem[] }
```

### WebView ? Host
```typescript
// Switch work item
{ type: 'switch', payload: { workItemId: string } }

// Create work item
{ type: 'create', payload: { workItemId: string, profile: string } }

// Refresh request
{ type: 'refresh' }
```

## Project Structure

```
golazo-webview/
??? package.json
??? vite.config.ts
??? src/
?   ??? main.tsx           # Entry point
?   ??? App.tsx            # Root component
?   ??? components/
?   ?   ??? Header.tsx
?   ?   ??? PhaseIndicator.tsx
?   ?   ??? RoleList.tsx
?   ?   ??? Checklist.tsx
?   ?   ??? WorkItemSwitcher.tsx
?   ??? hooks/
?   ?   ??? useHostMessaging.ts
?   ??? styles/
?       ??? theme.css
??? dist/                  # Build output
    ??? index.html
    ??? assets/
```

## Out of Scope

- VS Code extension shell (GCP2-005a)
- Visual Studio extension shell (GCP2-005c)
- Agent/protocol (GCP2-001)

## Dependencies

- GCP2-003 (State schema for type definitions)

## Technical Notes

- React 18+
- TypeScript
- Vite for bundling
- CSS variables for theming
- No external runtime dependencies (all bundled)
