"""Live test for MCDEMO-002: Relationship Detection"""
from kustomapper.adapters.kusto_adapter import KustoAdapter
from kustomapper.analysis.relationship_detector import RelationshipDetector

def main():
    print("=== MCDEMO-002 Live Test ===")
    print("Cluster: https://accia.kusto.windows.net")
    print("Database: CUD\n")
    
    # Connect
    adapter = KustoAdapter()
    adapter.connect(cluster='https://accia.kusto.windows.net', database='CUD')
    print("Fetching tables...")
    tables = adapter.get_tables()
    print(f"Found {len(tables)} tables:")
    for i, t in enumerate(tables):
        print(f"  {i+1}. {t.name}")
    
    # Get columns for ALL tables
    print("\nLoading schema for ALL tables:")
    for t in tables:
        t.columns = adapter.get_table_schema(t.name)
        print(f"  - {t.name}: {len(t.columns)} columns")
    
    # Detect relationships
    print("\nDetecting relationships...")
    detector = RelationshipDetector(tables)
    rels = detector.detect_all()
    
    print(f"\nFound {len(rels)} relationships:")
    for r in rels:
        print(f"  {r.source_table}.{r.source_column} -> {r.target_table}.{r.target_column} [{r.relationship_type.value}]")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()
