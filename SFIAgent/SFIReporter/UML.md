# Services View — Call Flow (UML Sequence Diagram)

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant App as SFIReporterApp
    participant Refresh as do_refresh()
    participant Data as data.py
    participant Client as S360Client
    participant Graph as GraphEndpoint
    participant Org as get_org_mapping()
    participant Owners as get_service_owners()
    participant Agg as aggregate_by_owner()
    participant Tree as _update_tables()

    User->>App: Click "Refresh Data"
    App->>App: _on_refresh() [A]
    App->>App: spawn background thread

    rect rgb(230, 245, 255)
    Note over Refresh: Background Thread
    App->>Refresh: do_refresh(alias) [B]

    %% Phase 1: Manager detection
    Refresh->>Data: get_client() [C]
    Data-->>Refresh: S360Client
    Refresh->>Client: get_default_landing_view(alias) [D]
    Client-->>Refresh: {SearchDataList: [...]}
    Refresh->>Refresh: is_manager_view(landing_view) [E]
    Note right of Refresh: ⚠️ BUG: Returns False for<br/>managers whose TeamGroup<br/>has no "(ALIAS)" pattern

    %% Phase 2: Fetch services & action items
    Refresh->>Data: get_user_team_info(alias) [F]
    Data-->>Refresh: (services, audience_ids)
    Refresh->>Data: get_all_programs() [G]
    Refresh->>Data: get_action_items_summary(audience_ids) [H]
    Refresh->>Data: get_detailed_action_items(audience_ids, kpi_ids) [I]

    %% Phase 3: Build service/kpi/program stats
    Refresh->>Refresh: Build service_stats, kpi_stats, program_stats

    %% Phase 4: Manager-only org mapping
    alt is_manager == True AND service_stats not empty
        Refresh->>Refresh: Extract manager_alias from TeamGroup name [J]
        Note right of Refresh: ⚠️ BUG: manager_alias=None<br/>if TeamGroup name lacks "(ALIAS)"

        Refresh->>Owners: get_service_owners(unique_names) [K]
        loop Each service (parallel)
            Owners->>Client: search(service_name) [L]
            Client-->>Owners: search results
            Owners->>Owners: parse_owners_field(Owners JSON) [M]
        end
        Owners-->>Refresh: {svc_name → [owner_names]}

        alt manager_alias is not None AND all_owners not empty
            Refresh->>Org: get_org_mapping(all_owners, manager_alias) [N]
            Org->>Data: get_client() [C]
            Org->>Client: get_org_tree(manager_alias) [O]
            Client->>Graph: get_org_tree(alias, depth=None) [P]
            Graph-->>Client: OrgTree
            Client-->>Org: OrgTree
            Org->>Org: _walk(tree, ()) — build name_lookup [Q]
            Note right of Org: ⚠️ BUG: Catches ALL exceptions<br/>silently → 100% Unknown Owner
            Org-->>Refresh: {owner → OrgAncestry(path=(...))}
        else manager_alias is None
            Note right of Refresh: org_mapping stays {}
        end

        Refresh->>Agg: aggregate_by_owner(items, svc_owners, org_mapping) [R]
        Agg->>Agg: _get_level1(mapped) for each owner [S]
        Agg-->>Refresh: owner_stats {owner → {count, sla, invalid_eta}}
    else is_manager == False
        Note right of Refresh: owner_stats stays {}
    end

    Refresh->>Refresh: _serialize_org_data_for_cache(data) [T]
    Refresh->>Refresh: write_cache(alias, serialized)
    end
    Refresh-->>App: data dict

    %% Phase 5: UI update on main thread
    App->>App: _on_refresh_complete(data) [U]
    App->>Tree: _update_tables(data) [V]

    alt is_manager AND owner_stats AND service_stats
        rect rgb(255, 245, 230)
        Note over Tree: Manager View — Hierarchical
        Tree->>Tree: Build svc_path_map (svc_id → path) [W]
        Tree->>Tree: Build root_groups nested dict [X]
        Tree->>Tree: _compute_group_stats(group) recursive [Y]
        Tree->>Tree: _insert_group(parent, name, group, depth, path) recursive [Z]
        Note right of Tree: 👤 icons, expand depth==0 only
        end
    else has services
        rect rgb(245, 255, 230)
        Note over Tree: IC View — Flat list
        Tree->>Tree: Insert services flat (no grouping) [AA]
        end
    end

    Tree-->>App: Treeview populated

    %% Drill-down on double-click
    User->>App: Double-click row in Services tree
    App->>App: _on_service_double_click(event) [AB]
    alt row is group (iid in _group_path_map)
        App->>App: collect_services_for_owner(path_prefix, svc_owners, org_mapping) [AC]
        App->>App: Filter detailed_items by matching services
    else row is service
        App->>App: filter_items_by_service(items, svc_id) [AD]
    end
    App->>App: DetailModal(title, items) [AE]
```

## Legend — Entry Points

| Ref | Function / Method | File | Line |
|-----|-------------------|------|------|
| **A** | `SFIReporterApp._on_refresh()` | `tk_app.py` | 3284 |
| **B** | `do_refresh(user_alias, on_status)` | `tk_app.py` | 625 |
| **C** | `get_client()` | `data.py` | 134 |
| **D** | `S360Client.get_default_landing_view(alias)` | `accia_s360/client.py` | 495 |
| **E** | `is_manager_view(landing_view)` | `tk_app.py` | 289 |
| **F** | `get_user_team_info(alias)` | `data.py` | 171 |
| **G** | `get_all_programs()` | `data.py` | 522 |
| **H** | `get_action_items_summary(audience_ids)` | `data.py` | 261 |
| **I** | `get_detailed_action_items(audience_ids, kpi_ids)` | `data.py` | 373 |
| **J** | Manager alias extraction (inline) | `tk_app.py` | 767–782 |
| **K** | `get_service_owners(unique_names)` | `tk_app.py` | 583 |
| **L** | `S360Client.search(service_name)` | `accia_s360/client.py` | ~150 |
| **M** | `parse_owners_field(owners_json)` | `tk_app.py` | 306 |
| **N** | `get_org_mapping(all_owners, manager_alias)` | `tk_app.py` | 329 |
| **O** | `S360Client.get_org_tree(alias)` | `accia_s360/client.py` | 97 |
| **P** | `GraphEndpoint.get_org_tree(alias, depth=None)` | `accia_s360/endpoints/graph.py` | 215 |
| **Q** | `_walk(node, parent_path)` (closure) | `tk_app.py` | 374 |
| **R** | `aggregate_by_owner(items, svc_owners, org_mapping)` | `tk_app.py` | 425 |
| **S** | `_get_level1(mapped)` (closure) | `tk_app.py` | 458 |
| **T** | `_serialize_org_data_for_cache(data)` | `tk_app.py` | 31 |
| **U** | `SFIReporterApp._on_refresh_complete(data)` | `tk_app.py` | 3307 |
| **V** | `SFIReporterApp._update_tables(data)` | `tk_app.py` | 2805 |
| **W** | `svc_path_map` construction (inline) | `tk_app.py` | 2859 |
| **X** | `root_groups` construction (inline) | `tk_app.py` | 2880 |
| **Y** | `_compute_group_stats(group)` (closure) | `tk_app.py` | 2908 |
| **Z** | `_insert_group(parent, name, group, depth, path)` (closure) | `tk_app.py` | 2933 |
| **AA** | IC flat insertion (inline) | `tk_app.py` | 2968 |
| **AB** | `SFIReporterApp._on_service_double_click(event)` | `tk_app.py` | 3020 |
| **AC** | `collect_services_for_owner(path_prefix, svc_owners, org_mapping)` | `tk_app.py` | 536 |
| **AD** | `filter_items_by_service(items, svc_id)` | `tk_app.py` | 837 |
| **AE** | `DetailModal(root, title, items, ...)` | `tk_app.py` | ~1100 |

## Known Bugs in Flow

| Bug | Location | Impact |
|-----|----------|--------|
| **`is_manager_view` false negative** | **E** (line 289) | If brentj's landing view has a TeamGroup but the detection fails, `is_manager=False` → IC flat view shown for a manager |
| **Silent exception in `get_org_tree`** | **Q** (line 366) | Any exception → all owners become "Unknown Owner" with no logging |
| **`manager_alias` extraction fragile** | **J** (line 773) | Requires `"Team Name (ALIAS)"` format — `None` if pattern absent → `org_mapping` stays `{}` |
| **Name format mismatch** | **Q** vs **M** | Graph `display_name` ("First Last") may differ from S360 owners ("Last, First") → lookups miss |
