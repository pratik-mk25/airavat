"""
Reactor Visual World Model Panel Module.
Renders predicted visual outcomes for AI actions in Streamlit GCS.
"""

import streamlit as st
import base64

def render_reactor_visual_panel(data):
    st.subheader("👁️ Reactor Visual World Model")
    
    metrics = data.get("metrics", {})
    visual_url = metrics.get("reactor_visual")
    
    if not visual_url:
        st.info("Waiting for Reactor visual prediction...")
        return
        
    st.caption(f"Predicted visual outcome for action: **{data.get('selected_action', 'Continue')}**")
    
    # Handle URL or Base64
    try:
        if isinstance(visual_url, str) and visual_url.startswith("http"):
            st.image(visual_url, use_container_width=True)
        else:
            # If base64 string or bytes
            if isinstance(visual_url, str):
                # Clean header prefix if present (e.g. data:image/png;base64,...)
                if "," in visual_url:
                    visual_url = visual_url.split(",")[1]
                img_data = base64.b64decode(visual_url)
            else:
                img_data = visual_url
            st.image(img_data, use_container_width=True)
    except Exception as e:
        st.error(f"Error rendering reactor visual: {e}")
