"""Streamlit app for SFI Reporter."""
import streamlit as st

from sfi_reporter.cache import (
    read_cache,
    write_cache,
    is_cache_valid,
    get_cache_age_minutes,
    clear_cache,
)
from sfi_reporter.data import get_current_user_alias, fetch_full_data


def main():
    """Main entry point for Streamlit app."""
    st.set_page_config(
        page_title="SFI Reporter",
        page_icon="📊",
        layout="wide",
    )
    
    st.title("📊 SFI Reporter")
    st.write("View Service Fabric Insights and Quality Engineering Insights for your services.")
    
    # Initialize session state
    if 'user_alias' not in st.session_state:
        detected = get_current_user_alias()
        st.session_state.user_alias = detected or ''
    
    # User alias input
    col1, col2 = st.columns([3, 1])
    with col1:
        user_alias = st.text_input(
            "User Alias",
            value=st.session_state.user_alias,
            help="Your Microsoft alias (e.g., 'brentj')",
        )
        st.session_state.user_alias = user_alias
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        refresh_clicked = st.button("🔄 Refresh Data", use_container_width=True)
    
    if not user_alias:
        st.warning("Please enter your user alias to continue.")
        return
    
    # Check cache
    cached_data = read_cache(user_alias)
    cache_valid = cached_data and is_cache_valid(cached_data)
    
    # Show cache status
    if cached_data:
        age_minutes = get_cache_age_minutes(cached_data)
        if age_minutes is not None:
            if age_minutes > 30:
                st.warning(f"⚠️ Cache is {age_minutes} minutes old")
            else:
                st.info(f"ℹ️ Cache is {age_minutes} minutes old")
    
    # Fetch data if needed
    if refresh_clicked or not cache_valid:
        with st.spinner("Fetching data from Services 360..."):
            try:
                data = fetch_full_data(user_alias)
                write_cache(user_alias, data)
                st.success("✅ Data refreshed successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error fetching data: {e}")
                if not cached_data:
                    return
    
    if not cached_data:
        st.info("No data available. Click 'Refresh Data' to fetch.")
        return
    
    # Display services
    services = cached_data.get('services', [])
    st.subheader(f"🔧 Services ({len(services)})")
    
    if services:
        st.dataframe(
            [
                {
                    'Name': s.get('Name', 'Unknown'),
                    'ID': s.get('Id', 'N/A'),
                }
                for s in services
            ],
            use_container_width=True,
        )
    else:
        st.info("No services found for this user.")
    
    # Display action items
    action_items = cached_data.get('action_items', {})
    summary_list = action_items.get('SummaryList', [])
    
    st.subheader(f"📋 Action Items ({len(summary_list)})")
    
    if summary_list:
        st.dataframe(
            [
                {
                    'Action Item': item.get('ActionItemName', 'Unknown'),
                    'ID': item.get('ActionItemId', 'N/A'),
                    'Total Count': item.get('TotalCount', 0),
                    'Out of SLA': item.get('OutOfSlaCount', 0),
                }
                for item in summary_list
            ],
            use_container_width=True,
        )
    else:
        st.success("✅ No action items! Great job!")
    
    # Clear cache button
    st.divider()
    if st.button("🗑️ Clear Cache"):
        if clear_cache(user_alias):
            st.success("Cache cleared!")
            st.rerun()


if __name__ == "__main__":
    main()
