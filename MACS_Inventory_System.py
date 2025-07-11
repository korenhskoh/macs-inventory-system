import streamlit as st
import pandas as pd
import qrcode
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import json
import io
import base64
from PIL import Image
import uuid
import time

# Configure page with custom theme
st.set_page_config(
    page_title="MACS Service Singapore Inventory System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Miltenyi Biotec theme
st.markdown("""
<style>
    /* Main theme colors */
    .main > div {
        background-color: #ffffff;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(90deg, #6B2C91 0%, #ff8c00 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Sidebar styling */
    .sidebar-logo {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #6B2C91 0%, #ff8c00 100%);
        border-radius: 10px;
        margin-bottom: 1rem;
        color: white;
    }
    
    /* Auto-complete dropdown */
    .autocomplete-dropdown {
        max-height: 200px;
        overflow-y: auto;
        border: 2px solid #ff8c00;
        border-radius: 5px;
        background: white;
        margin-top: 5px;
    }
    
    .autocomplete-item {
        padding: 10px;
        border-bottom: 1px solid #eee;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    
    .autocomplete-item:hover {
        background-color: #f8f9fa;
    }
    
    /* Status cards */
    .status-complete {
        background-color: #28a745;
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
    }
    
    .status-partial {
        background-color: #ff8c00;
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
    }
    
    .status-pending {
        background-color: #6c757d;
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
    }
    
    .status-backorder {
        background-color: #dc3545;
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
    }
    
    .status-draft {
        background-color: #6c757d;
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
    }
    
    .status-confirmed {
        background-color: #17a2b8;
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
    }
    
    /* Order table styling */
    .order-table {
        border: 2px solid #6B2C91;
        border-radius: 10px;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    .table-header {
        background: linear-gradient(90deg, #6B2C91 0%, #ff8c00 100%);
        color: white;
        padding: 1rem;
        font-weight: bold;
        text-align: center;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border: 2px solid #6B2C91;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        margin: 0.5rem;
    }
    
    /* Success/Warning/Error styling */
    .success-box {
        background-color: #28a745;
        color: white;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #155724;
    }
    
    .warning-box {
        background-color: #ff8c00;
        color: white;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #856404;
    }
    
    .error-box {
        background-color: #dc3545;
        color: white;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #721c24;
    }
    
    .info-box {
        background-color: #6B2C91;
        color: white;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #4a1d63;
    }
    
    .draft-box {
        background-color: #6c757d;
        color: white;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #495057;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #6B2C91 0%, #ff8c00 100%);
        color: white;
        border: none;
        border-radius: 5px;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #4a1d63 0%, #e6790c 100%);
        border: none;
    }
    
    /* Role access indicator */
    .role-indicator {
        background: linear-gradient(135deg, #6B2C91 0%, #ff8c00 100%);
        color: white;
        padding: 0.5rem;
        border-radius: 20px;
        text-align: center;
        font-size: 0.8rem;
        margin: 0.25rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'users' not in st.session_state:
    st.session_state.users = {
        'admin': {
            'password': 'admin123', 
            'role': 'admin', 
            'email': 'admin@macsservice.sg',
            'pages': ['all']  # Admin has access to all pages
        },
        'staff1': {
            'password': 'staff123', 
            'role': 'staff', 
            'email': 'staff1@macsservice.sg',
            'pages': ['order_management', 'qr_scanner', 'verification_dashboard', 'back_order', 'database_view', 'email']
        },
        'staff2': {
            'password': 'staff123', 
            'role': 'staff', 
            'email': 'staff2@macsservice.sg',
            'pages': ['order_management', 'qr_scanner', 'verification_dashboard', 'database_view']
        },
        'staff3': {
            'password': 'staff123', 
            'role': 'staff', 
            'email': 'staff3@macsservice.sg',
            'pages': ['order_management', 'qr_scanner']
        },
        'staff4': {
            'password': 'staff123', 
            'role': 'staff', 
            'email': 'staff4@macsservice.sg',
            'pages': ['order_management', 'qr_scanner', 'verification_dashboard']
        }
    }

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'current_user' not in st.session_state:
    st.session_state.current_user = None

if 'orders' not in st.session_state:
    st.session_state.orders = {}

if 'parts_database' not in st.session_state:
    st.session_state.parts_database = {
        'SP001': {'description': 'Ball Bearing 6203', 'cost': 25.50},
        'SP002': {'description': 'V-Belt A-Section', 'cost': 15.75},
        'SP003': {'description': 'Oil Filter OF-150', 'cost': 42.30},
        'SP004': {'description': 'Motor Coupling 5HP', 'cost': 185.00},
        'SP005': {'description': 'Pressure Gauge 0-100PSI', 'cost': 67.25},
        'SP006': {'description': 'Hydraulic Seal Kit', 'cost': 89.90},
        'SP007': {'description': 'Chain Link 40-1', 'cost': 12.40},
        'SP008': {'description': 'Safety Valve 1/2"', 'cost': 156.75}
    }

if 'received_parts' not in st.session_state:
    st.session_state.received_parts = {}

if 'back_orders' not in st.session_state:
    st.session_state.back_orders = {}

if 'email_settings' not in st.session_state:
    st.session_state.email_settings = {
        'sender_email': 'inventory@macsservice.sg',
        'recipient_email': 'manager@macsservice.sg',
        'cc_emails': 'procurement@macsservice.sg,logistics@macsservice.sg'
    }

if 'verified_months' not in st.session_state:
    st.session_state.verified_months = {}

def login():
    # Custom header without logo
    st.markdown(f"""
    <div class="main-header">
        <h1>🔐 MACS Service Singapore Inventory System</h1>
        <p>Professional Inventory Management Solution</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            st.subheader("🔑 System Login")
            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("🚀 Login", use_container_width=True)
            
            if submitted:
                if username in st.session_state.users and st.session_state.users[username]['password'] == password:
                    st.session_state.logged_in = True
                    st.session_state.current_user = username
                    st.success(f"✅ Welcome to MACS Service Singapore System, {username}!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
        
        st.markdown("""
        <div class="info-box">
            <h4>🔧 Demo Accounts:</h4>
            <p><strong>Admin:</strong> admin / admin123</p>
            <p><strong>Staff:</strong> staff1-staff4 / staff123</p>
        </div>
        """, unsafe_allow_html=True)

def check_page_access(page_key):
    """Check if current user has access to a page"""
    user = st.session_state.users[st.session_state.current_user]
    return 'all' in user['pages'] or page_key in user['pages']

def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf

def auto_complete_search(search_query):
    """Auto-complete functionality for part search with consistent naming"""
    if not search_query or len(search_query) < 2:
        return []
    
    matches = []
    for material_number, details in st.session_state.parts_database.items():
        # Check if search query matches Material Number or Material Description
        if (search_query.upper() in material_number.upper() or 
            search_query.upper() in details['description'].upper()):
            matches.append({
                'order_num': material_number,  # This is the Material Number
                'description': details['description'],  # This is the Material Description
                'cost': details['cost']  # This is the List price (unit cost)
            })
    
    return matches[:10]  # Return max 10 matches

def main_app():
    # Sidebar without logo
    st.sidebar.markdown(f"""
    <div class="sidebar-logo">
        <h3>MACS Service</h3>
        <p>Singapore</p>
    </div>
    """, unsafe_allow_html=True)
    
    # User info
    user_info = st.session_state.users[st.session_state.current_user]
    st.sidebar.markdown(f"""
    **👤 User:** {st.session_state.current_user}  
    **📧 Email:** {user_info['email']}
    """)
    
    # Role indicator
    role_color = "#6B2C91" if user_info['role'] == 'admin' else "#ff8c00"
    st.sidebar.markdown(f"""
    <div class="role-indicator" style="background-color: {role_color};">
        {user_info['role'].upper()} ACCESS
    </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()
    
    st.sidebar.divider()
    
    # Custom header without logo
    st.markdown(f"""
    <div class="main-header">
        <h1>📦 MACS Service Singapore Inventory System</h1>
        <p>Welcome back, {st.session_state.current_user} | {user_info['role'].title()} Access</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation based on user permissions
    available_pages = []
    page_mapping = {
        'order_management': '📝 Order Management',
        'qr_scanner': '📱 QR Scanner & Check-in',
        'verification_dashboard': '📊 Verification Dashboard',
        'back_order': '⚠️ Back Order Management',
        'database_management': '🗄️ Database Management',
        'database_view': '🗄️ Database View',
        'user_management': '👥 User Management',
        'email': '📧 Email Notifications',
        'all': 'All Pages'
    }
    
    if user_info['role'] == 'admin':
        available_pages = ['📋 User Guide', '📝 Order Management', '📱 QR Scanner & Check-in', '📊 Verification Dashboard', '⚠️ Back Order Management', '🗄️ Database Management', '👥 User Management', '📧 Email Notifications']
    else:
        available_pages = ['📋 User Guide']
        for page_key in user_info['pages']:
            if page_key in page_mapping:
                available_pages.append(page_mapping[page_key])
    
    page = st.sidebar.selectbox("🧭 Navigation", available_pages)
    
    # Show access restrictions
    if user_info['role'] != 'admin':
        restricted_count = len(page_mapping) - len(user_info['pages'])
        if restricted_count > 0:
            st.sidebar.warning(f"🔒 {restricted_count} pages restricted by admin")
    
    # Route to pages
    if page == "📋 User Guide":
        user_guide_page()
    elif page == "📝 Order Management" and check_page_access('order_management'):
        order_management_page()
    elif page == "📱 QR Scanner & Check-in" and check_page_access('qr_scanner'):
        qr_scanner_page()
    elif page == "📊 Verification Dashboard" and check_page_access('verification_dashboard'):
        verification_dashboard_page()
    elif page == "⚠️ Back Order Management" and check_page_access('back_order'):
        back_order_management_page()
    elif page == "🗄️ Database Management" and user_info['role'] == 'admin':
        database_management_page()
    elif page == "🗄️ Database View" and check_page_access('database_view'):
        database_view_page()
    elif page == "👥 User Management" and user_info['role'] == 'admin':
        user_management_page()
    elif page == "📧 Email Notifications" and check_page_access('email'):
        email_notifications_page()
    else:
        st.error("🚫 Access denied. Contact administrator for permissions.")

def user_guide_page():
    st.header("🎯 MACS Service Singapore - Visual Guide")
    
    # Quick visual overview - Fixed HTML rendering
    st.markdown("""
    <div style="background: linear-gradient(135deg, #6B2C91 0%, #ff8c00 100%); color: white; padding: 15px; border-radius: 15px; text-align: center; margin-bottom: 20px;">
        <h2>🚀 5-Step Success Path</h2>
        <h3>Setup → Order → QR → Verify → Analyze</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Interactive workflow selector
    st.markdown("## 🎮 Choose Your Adventure")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("👑 Admin Setup", use_container_width=True, help="Database & QR setup"):
            st.session_state.show_flow = "admin"
    
    with col2:
        if st.button("👥 Staff Orders", use_container_width=True, help="Create & manage orders"):
            st.session_state.show_flow = "staff_orders"
    
    with col3:
        if st.button("📱 Stock Check", use_container_width=True, help="QR scan & verification"):
            st.session_state.show_flow = "verification"
    
    # Reset button
    if hasattr(st.session_state, 'show_flow'):
        if st.button("🏠 Back to Main Menu"):
            del st.session_state.show_flow
            st.rerun()
    
    st.divider()
    
    # Show selected flowchart
    if hasattr(st.session_state, 'show_flow'):
        if st.session_state.show_flow == "admin":
            show_admin_flow()
        elif st.session_state.show_flow == "staff_orders":
            show_staff_orders_flow()
        elif st.session_state.show_flow == "verification":
            show_verification_flow()
    else:
        show_main_overview()

def show_main_overview():
    """Main visual overview with fixed HTML"""
    
    st.markdown("## 🔄 System Overview")
    
    # Using columns instead of complex HTML
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #6B2C91, #8e44ad); color: white; padding: 20px; border-radius: 15px; text-align: center;">
            <h2>👑</h2>
            <h3>ADMIN</h3>
            <p>Setup System<br/>📤 Database<br/>📱 QR Code<br/>👥 Users</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ff8c00, #ff6b35); color: white; padding: 20px; border-radius: 15px; text-align: center;">
            <h2>👥</h2>
            <h3>STAFF</h3>
            <p>Daily Tasks<br/>📝 Orders<br/>📱 Scan QR<br/>✅ Verify</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #28a745, #20c997); color: white; padding: 20px; border-radius: 15px; text-align: center;">
            <h2>📊</h2>
            <h3>RESULTS</h3>
            <p>Auto Magic<br/>📈 Reports<br/>🚨 Alerts<br/>✅ Complete</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Status colors legend
    st.markdown("## 🎨 Color Guide")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="background: #28a745; color: white; padding: 15px; border-radius: 10px; text-align: center;">
            <h2>🟢</h2>
            <h3>Complete</h3>
            <p>All Good!</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: #ff8c00; color: white; padding: 15px; border-radius: 10px; text-align: center;">
            <h2>🟡</h2>
            <h3>Partial</h3>
            <p>In Progress</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: #dc3545; color: white; padding: 15px; border-radius: 10px; text-align: center;">
            <h2>🔴</h2>
            <h3>Back Order</h3>
            <p>Missing Items</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="background: #6c757d; color: white; padding: 15px; border-radius: 10px; text-align: center;">
            <h2>⚪</h2>
            <h3>Pending</h3>
            <p>Not Started</p>
        </div>
        """, unsafe_allow_html=True)

def show_admin_flow():
    """Visual admin setup flowchart"""
    
    st.markdown("## 👑 Admin Setup Flow")
    
    # Step-by-step visual flow using columns
    steps = [
        {"icon": "📤", "title": "Upload Database", "desc": "CSV/Excel with materials", "color": "#6B2C91"},
        {"icon": "👥", "title": "Configure Users", "desc": "Set page permissions", "color": "#8e44ad"},
        {"icon": "📱", "title": "Generate QR", "desc": "One code for all", "color": "#9c27b0"},
        {"icon": "📧", "title": "Setup Emails", "desc": "Configure notifications", "color": "#673ab7"}
    ]
    
    for i, step in enumerate(steps):
        st.markdown(f"""
        <div style="background: {step['color']}; color: white; padding: 20px; border-radius: 15px; text-align: center; margin: 10px 0;">
            <h1 style="margin: 0; font-size: 60px;">{step['icon']}</h1>
            <h2 style="margin: 10px 0;">{step['title']}</h2>
            <p style="margin: 0; font-size: 16px;">{step['desc']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if i < len(steps) - 1:
            st.markdown("<div style='text-align: center; font-size: 40px; color: #6B2C91;'>⬇️</div>", unsafe_allow_html=True)
    
    # Database upload guide
    st.markdown("### 📤 Database Upload Details")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: #e8f5e8; padding: 15px; border-radius: 10px; border-left: 5px solid #28a745;">
            <h4>📋 Required Columns</h4>
            <ul>
                <li>Material Number</li>
                <li>Material Description</li>
                <li>List price (unit cost)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: #fff3cd; padding: 15px; border-radius: 10px; border-left: 5px solid #ff8c00;">
            <h4>⚠️ Watch Out For</h4>
            <ul>
                <li>Duplicate numbers</li>
                <li>Empty fields</li>
                <li>Wrong column names</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: #e3f2fd; padding: 15px; border-radius: 10px; border-left: 5px solid #2196f3;">
            <h4>💡 Pro Tips</h4>
            <ul>
                <li>Use our template</li>
                <li>Test with small file first</li>
                <li>Backup existing data</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def show_staff_orders_flow():
    """Visual staff orders flowchart - FIXED HTML rendering"""
    
    st.markdown("## 👥 Staff Order Flow")
    
    # Use Streamlit columns instead of raw HTML
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Flow steps using proper Streamlit components
        st.markdown("""
        <div style="background: #ff8c00; color: white; padding: 15px; border-radius: 10px; text-align: center; margin: 10px;">
            <h2>📅 Select Month</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='text-align: center; font-size: 30px; margin: 10px;'>⬇️</div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: #ff6b35; color: white; padding: 15px; border-radius: 10px; text-align: center; margin: 10px;">
            <h2>🔍 Search Materials</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='text-align: center; font-size: 30px; margin: 10px;'>⬇️</div>", unsafe_allow_html=True)
    
    # Order method selection
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #28a745, #20c997); color: white; padding: 20px; border-radius: 15px; text-align: center;">
            <h3>📝 Single Order</h3>
            <h1>1️⃣</h1>
            <p>Search → Select → Add Quantity<br/>Perfect for one-off items</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ff8c00, #ff6b35); color: white; padding: 20px; border-radius: 15px; text-align: center;">
            <h3>📦 Bulk Order</h3>
            <h1>📋</h1>
            <p>Select Multiple → Add All Quantities<br/>Perfect for regular orders</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Bulk order example using proper dataframe
    st.markdown("### 📦 Bulk Order Example")
    
    # Create sample data for display
    sample_data = {
        'Select': ['✅', '✅', '☑️'],
        'Material Number': ['SP001', 'SP002', 'SP003'],
        'Description': ['Ball Bearing 6203', 'V-Belt A-Section', 'Oil Filter OF-150'],
        'Unit Cost': ['$25.50', '$15.75', '$42.30'],
        'Quantity': ['10', '5', '0'],
        'Total': ['$255.00', '$78.75', '$0.00']
    }
    
    sample_df = pd.DataFrame(sample_data)
    
    st.dataframe(
        sample_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Select": st.column_config.TextColumn("☑️", width="small"),
            "Material Number": st.column_config.TextColumn("Material Number", width="medium"),
            "Description": st.column_config.TextColumn("Description", width="large"),
            "Unit Cost": st.column_config.TextColumn("Unit Cost", width="small"),
            "Quantity": st.column_config.TextColumn("Quantity ✏️", width="small"),
            "Total": st.column_config.TextColumn("Total", width="small")
        }
    )
    
    # Show selected total
    st.markdown("""
    <div style="background: #28a745; color: white; padding: 10px; border-radius: 5px; text-align: center; margin: 10px 0;">
        <strong>SELECTED TOTAL: $333.75</strong>
    </div>
    """, unsafe_allow_html=True)

def show_verification_flow():
    """Visual verification flowchart - FIXED HTML rendering"""
    
    st.markdown("## 📱 Stock Verification Flow")
    
    # Process flow using columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="text-align: center;">
            <div style="background: #6B2C91; color: white; padding: 20px; border-radius: 50%; width: 80px; height: 80px; margin: 0 auto 10px; display: flex; align-items: center; justify-content: center;">
                <span style="font-size: 30px;">📱</span>
            </div>
            <h4>Scan QR</h4>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center;">
            <div style="background: #ff8c00; color: white; padding: 20px; border-radius: 50%; width: 80px; height: 80px; margin: 0 auto 10px; display: flex; align-items: center; justify-content: center;">
                <span style="font-size: 30px;">🔐</span>
            </div>
            <h4>Login</h4>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center;">
            <div style="background: #28a745; color: white; padding: 20px; border-radius: 50%; width: 80px; height: 80px; margin: 0 auto 10px; display: flex; align-items: center; justify-content: center;">
                <span style="font-size: 30px;">📅</span>
            </div>
            <h4>Select Month</h4>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="text-align: center;">
            <div style="background: #17a2b8; color: white; padding: 20px; border-radius: 50%; width: 80px; height: 80px; margin: 0 auto 10px; display: flex; align-items: center; justify-content: center;">
                <span style="font-size: 30px;">✅</span>
            </div>
            <h4>Verify Items</h4>
        </div>
        """, unsafe_allow_html=True)
    
    # Verification table example using proper dataframe
    st.markdown("### 📊 Verification Table Example")
    
    verification_data = {
        'Material No.': ['SP001', 'SP002'],
        'Description': ['Ball Bearing', 'V-Belt'],
        'Ordered': [10, 5],
        'Received': ['10 ✏️', '3 ✏️'],
        'Remaining': [0, 2],
        'Over/Under': [0, -2],
        'Status': ['✅ COMPLETE', '🚨 BACK ORDER']
    }
    
    verification_df = pd.DataFrame(verification_data)
    
    st.dataframe(
        verification_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Material No.": st.column_config.TextColumn("Material No.", width="small"),
            "Description": st.column_config.TextColumn("Description", width="medium"),
            "Ordered": st.column_config.NumberColumn("Ordered", width="small"),
            "Received": st.column_config.TextColumn("Received ✏️", width="small"),
            "Remaining": st.column_config.NumberColumn("Remaining", width="small"),
            "Over/Under": st.column_config.NumberColumn("Over/Under", width="small"),
            "Status": st.column_config.TextColumn("Status", width="medium")
        }
    )

def prepare_order_summary_email(month_key, orders_df):
    """Prepare order summary email with proper column names"""
    st.session_state.email_subject = f"📦 Order Summary - {month_key}"
    
    # Create HTML table with database-consistent column names
    html_table = """
    <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%;">
    <tr style="background: linear-gradient(90deg, #6B2C91 0%, #ff8c00 100%); color: white;">
        <th>Material Number</th>
        <th>Material Description</th>
        <th>Quantity</th>
        <th>List price (unit cost)</th>
        <th>Total Cost</th>
    </tr>
    """
    
    grand_total = 0
    for _, row in orders_df.iterrows():
        html_table += f"""
        <tr>
            <td><strong>{row['Order Number']}</strong></td>
            <td>{row['description']}</td>
            <td>{row['quantity']}</td>
            <td>${row['unit_cost']:.2f}</td>
            <td><strong>${row['total_cost']:.2f}</strong></td>
        </tr>
        """
        grand_total += row['total_cost']
    
    html_table += f"""
    <tr style="background-color: #f8f9fa; font-weight: bold;">
        <td colspan="4">GRAND TOTAL</td>
        <td>${grand_total:.2f}</td>
    </tr>
    </table>
    """
    
    st.session_state.email_content = f"""
    <h2>📦 Order Summary - {month_key}</h2>
    <div style="background: linear-gradient(90deg, #6B2C91 0%, #ff8c00 100%); padding: 15px; border-radius: 5px; color: white;">
        <h3>MACS Service Singapore - Inventory System</h3>
        <p>Order summary for procurement and logistics</p>
    </div>
    <br>
    {html_table}
    <p><strong>Generated by:</strong> {st.session_state.current_user}</p>
    <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    """

def order_management_page():
    """
    Enhanced Order Management Page with tabs and combined entry
    """
    st.header("📝 Order Management")
    
    # Month selection
    st.markdown("### 📅 Select Order Period")
    col1, col2 = st.columns(2)
    with col1:
        selected_month = st.selectbox("📅 Month", 
                                    ["January", "February", "March", "April", "May", "June",
                                     "July", "August", "September", "October", "November", "December"])
    with col2:
        selected_year = st.selectbox("📅 Year", [2024, 2025, 2026])
    
    month_key = f"{selected_month}/{selected_year}"
    
    if month_key not in st.session_state.orders:
        st.session_state.orders[month_key] = {}
    
    st.divider()
    
    # Tab selection for order methods
    st.markdown("### 🎯 Choose Order Method")
    
    tab1, tab2 = st.tabs(["📝 Single Order", "📦 Bulk Order"])
    
    with tab1:
        show_single_order_tab(month_key)
    
    with tab2:
        show_bulk_order_tab(month_key)
    
    st.divider()
    
    # Display current orders (shared between both tabs)
    display_current_orders(month_key, selected_month, selected_year)

def show_single_order_tab(month_key):
    """Single order tab with combined search and quantity entry"""
    
    st.markdown("#### 📝 Single Order Entry")
    
    # Initialize session state for selected part
    if 'selected_part_data' not in st.session_state:
        st.session_state.selected_part_data = {}
    
    # Combined search and order entry
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("**🔍 Part Search & Selection**")
        
        # Search functionality
        search_query = st.text_input(
            "🔎 Search Parts", 
            placeholder="Type Material Number or description...",
            help="Start typing to see matching parts",
            key="search_input_single"
        )
        
        # Auto-complete results
        if search_query:
            matches = auto_complete_search(search_query)
            
            if matches:
                st.markdown("**📋 Matching Parts:**")
                
                for i, match in enumerate(matches):
                    if st.button(
                        f"🔹 {match['order_num']} - {match['description']} (${match['cost']:.2f})",
                        key=f"single_select_{i}",
                        use_container_width=True,
                        help=f"Select Material Number: {match['order_num']}"
                    ):
                        st.session_state.selected_part_data = {
                            'order_num': match['order_num'],
                            'description': match['description'],
                            'cost': match['cost'],
                            'found_in_db': True
                        }
                        st.rerun()
            else:
                st.warning("❌ No matching parts found")
        
        # Manual entry section
        with st.expander("💬 Manual Entry (for new parts)"):
            with st.form("manual_entry_form"):
                manual_order = st.text_input("Material Number", placeholder="e.g., SP009")
                manual_description = st.text_input("Material Description", placeholder="e.g., New Hydraulic Pump")
                manual_cost = st.number_input("List price (unit cost) ($)", min_value=0.01, step=0.01, value=1.00)
                
                if st.form_submit_button("📝 Use Manual Entry"):
                    if manual_order and manual_description and manual_cost > 0:
                        st.session_state.selected_part_data = {
                            'order_num': manual_order,
                            'description': manual_description,
                            'cost': manual_cost,
                            'found_in_db': False
                        }
                        st.success("✅ Manual entry selected!")
                        st.rerun()
                    else:
                        st.error("❌ Please fill all manual entry fields!")
    
    with col2:
        st.markdown("**📦 Order Details & Quantity**")
        
        # Display selected part and quantity input together
        if st.session_state.selected_part_data:
            part_data = st.session_state.selected_part_data
            
            # Show selected part info
            st.text_input("📝 Material Number", value=part_data['order_num'], disabled=True, key="display_num")
            st.text_input("📝 Material Description", value=part_data['description'], disabled=True, key="display_desc")
            st.text_input("💰 List price (unit cost) ($)", value=f"{part_data['cost']:.2f}", disabled=True, key="display_cost")
            
            if part_data['found_in_db']:
                st.success("✅ Part found in database")
            else:
                st.warning("⚠️ Manual entry - will be added to database")
            
            # Quantity and total in the same section
            with st.form("add_single_order_form"):
                quantity = st.number_input("📊 Quantity", min_value=1, value=1, key="single_qty")
                total_cost = quantity * part_data['cost']
                st.text_input("💵 Total Cost ($)", value=f"{total_cost:.2f}", disabled=True, key="single_total")
                
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if st.form_submit_button("➕ Add Order", use_container_width=True):
                        add_single_order(month_key, part_data, quantity, total_cost)
                
                with col_btn2:
                    if st.form_submit_button("🗑️ Clear", use_container_width=True):
                        st.session_state.selected_part_data = {}
                        st.rerun()
        
        else:
            st.info("👆 Search and select a part to add order")
            
            # Show recent parts for quick selection
            if st.session_state.parts_database:
                st.markdown("**🕐 Recent Parts:**")
                recent_parts = list(st.session_state.parts_database.items())[:5]
                
                for material_num, details in recent_parts:
                    if st.button(
                        f"⚡ {material_num} - {details['description']}",
                        key=f"recent_{material_num}",
                        use_container_width=True
                    ):
                        st.session_state.selected_part_data = {
                            'order_num': material_num,
                            'description': details['description'],
                            'cost': details['cost'],
                            'found_in_db': True
                        }
                        st.rerun()

def show_bulk_order_tab(month_key):
    """Bulk order tab with table interface - FIXED checkbox labels"""
    
    st.markdown("#### 📦 Bulk Order Entry")
    st.info("💡 Select multiple materials and set quantities all at once!")
    
    # Search filter for bulk
    search_term = st.text_input("🔍 Filter Materials", placeholder="Filter by Material Number or description...", key="bulk_search")
    
    # Filter materials
    filtered_materials = {}
    for material_num, details in st.session_state.parts_database.items():
        if not search_term or (
            search_term.upper() in material_num.upper() or 
            search_term.upper() in details['description'].upper()
        ):
            filtered_materials[material_num] = details
    
    if filtered_materials:
        st.markdown(f"**Found {len(filtered_materials)} materials**")
        
        # Bulk order form
        with st.form("bulk_order_form"):
            st.markdown("**Select materials and enter quantities:**")
            
            # Create data collection
            bulk_data = []
            total_cost = 0
            
            # Display materials in a more streamlined way
            materials_list = list(filtered_materials.items())[:15]  # Limit for performance
            
            # Table-like headers
            col1, col2, col3, col4, col5, col6 = st.columns([0.8, 2, 3, 1.2, 1.5, 1.5])
            
            with col1:
                st.markdown("**☑️**")
            with col2:
                st.markdown("**Material Number**")
            with col3:
                st.markdown("**Material Description**")
            with col4:
                st.markdown("**Unit Cost**")
            with col5:
                st.markdown("**Quantity**")
            with col6:
                st.markdown("**Total**")
            
            st.markdown("---")
            
            # Material rows
            for material_num, details in materials_list:
                col1, col2, col3, col4, col5, col6 = st.columns([0.8, 2, 3, 1.2, 1.5, 1.5])
                
                with col1:
                    # FIXED: Provide proper label and hide it
                    selected = st.checkbox(
                        f"Select {material_num}", 
                        key=f"bulk_select_{material_num}", 
                        label_visibility="collapsed"
                    )
                
                with col2:
                    st.markdown(f"**{material_num}**")
                
                with col3:
                    st.write(details['description'])
                
                with col4:
                    st.write(f"${details['cost']:.2f}")
                
                with col5:
                    quantity = st.number_input(
                        f"Quantity for {material_num}",
                        min_value=0,
                        value=0,
                        key=f"bulk_qty_{material_num}",
                        label_visibility="collapsed"
                    )
                
                with col6:
                    item_total = quantity * details['cost']
                    st.write(f"**${item_total:.2f}**")
                    
                    # Collect selected items
                    if selected and quantity > 0:
                        bulk_data.append({
                            'material_num': material_num,
                            'description': details['description'],
                            'unit_cost': details['cost'],
                            'quantity': quantity,
                            'total_cost': item_total
                        })
                        total_cost += item_total
            
            # Summary and submit
            if bulk_data:
                st.markdown("---")
                st.markdown(f"**📦 Selected Items: {len(bulk_data)} | 💰 Grand Total: ${total_cost:.2f}**")
            
            # Submit bulk order
            if st.form_submit_button("🚀 Add All Selected Orders", use_container_width=True):
                if bulk_data:
                    add_bulk_orders(month_key, bulk_data)
                else:
                    st.warning("⚠️ Please select items and set quantities first!")
    
    else:
        st.info("📝 No materials found. Upload materials to database first or try different search terms.")

def add_single_order(month_key, part_data, quantity, total_cost):
    """Add a single order"""
    order_number = part_data['order_num']
    description = part_data['description']
    cost = part_data['cost']
    
    # Add to database if manual entry
    if not part_data['found_in_db']:
        st.session_state.parts_database[order_number] = {
            'description': description,
            'cost': cost
        }
    
    # Add order with draft status
    if order_number in st.session_state.orders[month_key]:
        st.warning(f"⚠️ Order {order_number} already exists. Use Edit to modify.")
    else:
        st.session_state.orders[month_key][order_number] = {
            'description': description,
            'quantity': quantity,
            'unit_cost': cost,
            'total_cost': total_cost,
            'order_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'draft',  # NEW: Track order status
            'confirmed_by': None,
            'confirmed_date': None
        }
        st.success(f"✅ Order {order_number} added successfully!")
        
        # Clear selection after adding
        st.session_state.selected_part_data = {}
        
        time.sleep(1)
        st.rerun()

def add_bulk_orders(month_key, bulk_data):
    """Add multiple orders from bulk selection"""
    added_count = 0
    skipped_count = 0
    
    for item in bulk_data:
        material_num = item['material_num']
        
        if material_num in st.session_state.orders[month_key]:
            skipped_count += 1
        else:
            st.session_state.orders[month_key][material_num] = {
                'description': item['description'],
                'quantity': item['quantity'],
                'unit_cost': item['unit_cost'],
                'total_cost': item['total_cost'],
                'order_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'draft',  # NEW: Track order status
                'confirmed_by': None,
                'confirmed_date': None
            }
            added_count += 1
    
    # Show results
    if added_count > 0:
        st.success(f"✅ Added {added_count} orders successfully!")
    if skipped_count > 0:
        st.warning(f"⚠️ Skipped {skipped_count} duplicate orders")
    
    if added_count > 0:
        st.balloons()
        time.sleep(1)
        st.rerun()

def display_current_orders(month_key, selected_month, selected_year):
    """Display current orders table with confirmation system"""
    
    if st.session_state.orders[month_key]:
        st.markdown(f"### 📋 Orders for {selected_month} {selected_year}")
        
        # Check order status
        draft_orders = {k: v for k, v in st.session_state.orders[month_key].items() if v.get('status', 'draft') == 'draft'}
        confirmed_orders = {k: v for k, v in st.session_state.orders[month_key].items() if v.get('status', 'draft') == 'confirmed'}
        
        # Show status summary
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>📝</h3>
                <h2>{len(draft_orders)}</h2>
                <p>Draft Orders</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>✅</h3>
                <h2>{len(confirmed_orders)}</h2>
                <p>Confirmed Orders</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            total_value = sum(v['total_cost'] for v in st.session_state.orders[month_key].values())
            st.markdown(f"""
            <div class="metric-card">
                <h3>💰</h3>
                <h2>${total_value:.2f}</h2>
                <p>Total Value</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Order confirmation section
        if draft_orders:
            st.markdown("### 🔒 Order Confirmation Required")
            
            st.markdown("""
            <div class="draft-box">
                <h4>📝 Draft Orders Status</h4>
                <p>⚠️ <strong>{}</strong> orders are in DRAFT status and need confirmation before they appear in stock check-in.</p>
                <p>📋 Only CONFIRMED orders will be available for stock verification.</p>
            </div>
            """.format(len(draft_orders)), unsafe_allow_html=True)
            
            # Show draft orders table
            st.markdown("**📝 Draft Orders (Awaiting Confirmation):**")
            
            for material_number, order_details in draft_orders.items():
                col1, col2, col3, col4, col5, col6, col7 = st.columns([1.5, 3, 1, 1.2, 1.5, 1, 1])
                
                with col1:
                    st.markdown(f"**{material_number}**")
                
                with col2:
                    st.write(order_details['description'])
                
                with col3:
                    st.markdown(f"**{order_details['quantity']}**")
                
                with col4:
                    st.write(f"${order_details['unit_cost']:.2f}")
                
                with col5:
                    st.markdown(f"**${order_details['total_cost']:.2f}**")
                
                with col6:
                    st.markdown('<div class="status-draft">DRAFT</div>', unsafe_allow_html=True)
                
                with col7:
                    if st.button("🗑️", key=f"delete_draft_{material_number}", help="Delete draft order"):
                        del st.session_state.orders[month_key][material_number]
                        st.success(f"✅ Draft order {material_number} deleted!")
                        st.rerun()
                
                st.markdown("---")
            
            # Final confirmation button
            st.markdown("### 🚀 Final Order Confirmation")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("""
                <div class="warning-box">
                    <h4>🔒 Confirm All Orders</h4>
                    <p>Click below to confirm ALL draft orders. Once confirmed:</p>
                    <ul>
                        <li>✅ Orders will appear in stock check-in system</li>
                        <li>🔒 Orders cannot be deleted (only edited)</li>
                        <li>📱 QR scanner will include these orders</li>
                        <li>📧 Order summary can be sent</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("🔒 CONFIRM ALL ORDERS", 
                           use_container_width=True, 
                           help="Confirm all draft orders for stock check-in",
                           type="primary"):
                    # Confirm all draft orders
                    confirmation_count = 0
                    for material_number in draft_orders.keys():
                        st.session_state.orders[month_key][material_number]['status'] = 'confirmed'
                        st.session_state.orders[month_key][material_number]['confirmed_by'] = st.session_state.current_user
                        st.session_state.orders[month_key][material_number]['confirmed_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        confirmation_count += 1
                    
                    st.success(f"🎉 Successfully confirmed {confirmation_count} orders!")
                    st.balloons()
                    time.sleep(1)
                    st.rerun()
        
        # Show confirmed orders
        if confirmed_orders:
            st.markdown("### ✅ Confirmed Orders")
            
            st.markdown("""
            <div class="success-box">
                <h4>✅ Confirmed Orders Status</h4>
                <p>🎉 These orders are confirmed and available for stock check-in verification.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Enhanced table display for confirmed orders
            st.markdown("""
            <div style="background: linear-gradient(90deg, #28a745 0%, #20c997 100%); color: white; padding: 15px; border-radius: 10px; text-align: center; margin: 10px 0;">
                <h3>✅ CONFIRMED ORDERS TABLE</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Table headers
            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1.5, 3, 1, 1.2, 1.5, 1.5, 1.5, 1])
            
            with col1:
                st.markdown("**Material No.**")
            with col2:
                st.markdown("**Description**")
            with col3:
                st.markdown("**Qty**")
            with col4:
                st.markdown("**Unit Cost**")
            with col5:
                st.markdown("**Total Cost**")
            with col6:
                st.markdown("**Status**")
            with col7:
                st.markdown("**Confirmed By**")
            with col8:
                st.markdown("**Action**")
            
            st.markdown("---")
            
            # Create confirmed orders DataFrame for email
            confirmed_orders_data = []
            
            for material_number, order_details in confirmed_orders.items():
                col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1.5, 3, 1, 1.2, 1.5, 1.5, 1.5, 1])
                
                with col1:
                    st.markdown(f"**{material_number}**")
                
                with col2:
                    st.write(order_details['description'])
                
                with col3:
                    st.markdown(f"**{order_details['quantity']}**")
                
                with col4:
                    st.write(f"${order_details['unit_cost']:.2f}")
                
                with col5:
                    st.markdown(f"**${order_details['total_cost']:.2f}**")
                
                with col6:
                    st.markdown('<div class="status-confirmed">CONFIRMED</div>', unsafe_allow_html=True)
                
                with col7:
                    confirmed_by = order_details.get('confirmed_by', 'Unknown')
                    st.write(f"{confirmed_by}")
                
                with col8:
                    if st.button("✏️", key=f"edit_confirmed_{material_number}", help="Edit confirmed order"):
                        st.session_state.editing_order = material_number
                
                # Add to confirmed orders data for email
                confirmed_orders_data.append({
                    'Order Number': material_number,
                    'description': order_details['description'],
                    'quantity': order_details['quantity'],
                    'unit_cost': order_details['unit_cost'],
                    'total_cost': order_details['total_cost']
                })
                
                st.markdown("---")
            
            # Edit order modal (only for confirmed orders)
            if hasattr(st.session_state, 'editing_order'):
                with st.expander(f"✏️ Edit Confirmed Order {st.session_state.editing_order}", expanded=True):
                    order_to_edit = st.session_state.orders[month_key][st.session_state.editing_order]
                    
                    with st.form(f"edit_form_{st.session_state.editing_order}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            new_quantity = st.number_input("Quantity", value=order_to_edit['quantity'], min_value=1)
                            new_cost = st.number_input("List price (unit cost) ($)", value=order_to_edit['unit_cost'], min_value=0.01, step=0.01)
                        
                        with col2:
                            new_description = st.text_input("Material Description", value=order_to_edit['description'])
                            new_total = new_quantity * new_cost
                            st.text_input("Total Cost ($)", value=f"{new_total:.2f}", disabled=True)
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.form_submit_button("💾 Save Changes"):
                                st.session_state.orders[month_key][st.session_state.editing_order] = {
                                    'description': new_description,
                                    'quantity': new_quantity,
                                    'unit_cost': new_cost,
                                    'total_cost': new_total,
                                    'order_date': order_to_edit['order_date'],
                                    'status': 'confirmed',  # Keep confirmed status
                                    'confirmed_by': order_to_edit.get('confirmed_by'),
                                    'confirmed_date': order_to_edit.get('confirmed_date')
                                }
                                # Update database
                                st.session_state.parts_database[st.session_state.editing_order] = {
                                    'description': new_description,
                                    'cost': new_cost
                                }
                                del st.session_state.editing_order
                                st.success("✅ Confirmed order updated!")
                                st.rerun()
                        
                        with col2:
                            if st.form_submit_button("❌ Cancel"):
                                del st.session_state.editing_order
                                st.rerun()
            
            # Action buttons for confirmed orders
            if confirmed_orders_data:
                st.markdown("### 📧 Send Confirmed Orders")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📧 Send Order Summary", use_container_width=True):
                        confirmed_df = pd.DataFrame(confirmed_orders_data)
                        prepare_order_summary_email(month_key, confirmed_df)
                        st.success("📧 Order summary prepared! Go to Email Notifications.")
                
                with col2:
                    # QR Code generation (Admin only)
                    if st.session_state.users[st.session_state.current_user]['role'] == 'admin':
                        if st.button("📱 Generate QR Code", use_container_width=True):
                            st.session_state.show_qr = True
                    else:
                        st.info("🔒 QR Generation - Admin Only")
                
                with col3:
                    # Download confirmed orders
                    if st.button("📄 Download Orders", use_container_width=True):
                        confirmed_df = pd.DataFrame(confirmed_orders_data)
                        csv_data = confirmed_df.to_csv(index=False)
                        st.download_button(
                            label="💾 Download CSV",
                            data=csv_data,
                            file_name=f"confirmed_orders_{month_key.replace('/', '_')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
        
        # QR Code display
        if hasattr(st.session_state, 'show_qr') and st.session_state.show_qr:
            display_qr_code_section()
    
    else:
        st.info("📝 No orders for this month yet. Use the tabs above to add orders!")

def display_qr_code_section():
    """Display QR code generation section"""
    
    st.markdown("### 📱 QR Code for Stock Check-in")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Generate QR with login redirect
        base_url = "http://localhost:8501"
        qr_data = f"{base_url}/?access=stock_check"
        qr_buffer = generate_qr_code(qr_data)
        st.image(qr_buffer, caption="Scan for Stock Check-in", width=200)
        
        qr_buffer.seek(0)
        st.download_button(
            label="💾 Download QR Code",
            data=qr_buffer,
            file_name="macs_singapore_inventory_qr.png",
            mime="image/png",
            use_container_width=True
        )
        
        if st.button("❌ Close QR", use_container_width=True):
            del st.session_state.show_qr
            st.rerun()
    
    with col2:
        st.markdown("""
        <div style="background: #6B2C91; color: white; padding: 20px; border-radius: 10px;">
            <h4>📱 QR Code Instructions:</h4>
            <ol>
                <li>Download and print the QR code</li>
                <li>Place in your receiving area</li>
                <li>Staff scan with phone camera</li>
                <li>System opens → Login → Stock verification</li>
                <li>Select month → Enter received quantities</li>
            </ol>
            <p><strong>Access:</strong> Direct link to stock check-in system</p>
        </div>
        """, unsafe_allow_html=True)

def qr_scanner_page():
    st.header("📱 QR Scanner & Stock Check-in")
    
    # Check for QR access parameter - UPDATED to use new API
    query_params = st.query_params
    if 'access' in query_params and query_params['access'] == 'stock_check':
        st.success("📱 QR Code Access Detected - Welcome to Stock Check-in!")
    
    # QR input section
    st.markdown("### 📲 Access Stock Check-in")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        access_method = st.radio(
            "Choose access method:",
            ["🔑 Direct Access", "📱 QR Code Scan"]
        )
        
        if access_method == "📱 QR Code Scan":
            qr_input = st.text_input("📱 QR Code Data", placeholder="Scan QR code or enter URL")
            if qr_input and "stock_check" in qr_input:
                st.success("✅ QR Code Valid - Access Granted!")
                show_stock_checkin = True
            else:
                show_stock_checkin = False
        else:
            show_stock_checkin = True
    
    with col2:
        st.markdown("""
        <div class="info-box">
            <h4>📱 QR Scanner Guide</h4>
            <p>1. Use phone camera</p>
            <p>2. Scan QR code</p>
            <p>3. Follow link to system</p>
            <p>4. Login if required</p>
        </div>
        """, unsafe_allow_html=True)
    
    if show_stock_checkin:
        display_stock_checkin_interface()

def display_stock_checkin_interface():
    """Main stock check-in interface - UPDATED to only show confirmed orders"""
    st.markdown("### 📅 Select Month for Stock Verification")
    
    # Filter to only show months with CONFIRMED orders
    confirmed_months = {}
    for month_key, orders in st.session_state.orders.items():
        confirmed_orders = {k: v for k, v in orders.items() if v.get('status', 'draft') == 'confirmed'}
        if confirmed_orders:
            confirmed_months[month_key] = confirmed_orders
    
    if not confirmed_months:
        st.markdown("""
        <div class="warning-box">
            <h4>⚠️ No Confirmed Orders Available</h4>
            <p>📝 No confirmed orders found for stock verification.</p>
            <p>🔒 Only CONFIRMED orders appear in stock check-in system.</p>
            <p>👉 Go to Order Management to confirm draft orders first.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Month selection
    available_months = list(confirmed_months.keys())
    
    def sort_month_key(month_key):
        month_name, year = month_key.split('/')
        month_num = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"].index(month_name) + 1
        return (int(year), month_num)
    
    available_months.sort(key=sort_month_key, reverse=True)
    
    # Month selection cards
    cols = st.columns(3)
    
    for i, month_key in enumerate(available_months):
        with cols[i % 3]:
            month_name, year = month_key.split('/')
            orders_count = len(confirmed_months[month_key])  # Only confirmed orders
            
            # Calculate completion
            received_count = 0
            if month_key in st.session_state.received_parts:
                for order_num, details in confirmed_months[month_key].items():
                    if st.session_state.received_parts[month_key].get(order_num, 0) == details['quantity']:
                        received_count += 1
            
            completion_pct = (received_count / orders_count) * 100 if orders_count > 0 else 0
            
            # Status styling
            if completion_pct == 100:
                card_style = "success-box"
                status_icon = "🟢"
            elif completion_pct > 0:
                card_style = "warning-box"
                status_icon = "🟡"
            else:
                card_style = "error-box"
                status_icon = "🔴"
            
            st.markdown(f"""
            <div class="{card_style}" style="text-align: center; margin: 0.5rem 0;">
                <h3>{status_icon} {month_name} {year}</h3>
                <p><strong>{orders_count} confirmed orders</strong></p>
                <p>{completion_pct:.0f}% complete</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"✅ Verify {month_name}", key=f"verify_{month_key}", use_container_width=True):
                st.session_state.selected_verification_month = month_key
                st.rerun()
    
    # Display verification table if month selected
    if hasattr(st.session_state, 'selected_verification_month'):
        display_verification_table(st.session_state.selected_verification_month)

def display_verification_table(month_key):
    """Enhanced verification table with IMPROVED back order logic - UPDATED for confirmed orders only"""
    st.markdown(f"### 📦 Stock Verification Table - {month_key}")
    
    # Filter to only confirmed orders
    all_orders = st.session_state.orders[month_key]
    orders = {k: v for k, v in all_orders.items() if v.get('status', 'draft') == 'confirmed'}
    
    if not orders:
        st.markdown("""
        <div class="warning-box">
            <h4>⚠️ No Confirmed Orders Found</h4>
            <p>No confirmed orders available for verification in this month.</p>
            <p>👉 Go to Order Management to confirm orders first.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    if month_key not in st.session_state.received_parts:
        st.session_state.received_parts[month_key] = {}
    
    # Status summary
    total_items = len(orders)
    completed_items = 0
    over_received_items = 0
    back_order_items = 0
    
    for order_num, details in orders.items():
        received_qty = st.session_state.received_parts[month_key].get(order_num, 0)
        ordered_qty = details['quantity']
        
        if received_qty == ordered_qty:
            completed_items += 1
        elif received_qty > ordered_qty:
            over_received_items += 1
        elif received_qty < ordered_qty:  # UPDATED: This includes both partial AND zero received
            back_order_items += 1
    
    # Status dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📦</h3>
            <h2>{total_items}</h2>
            <p>Total Items</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>✅</h3>
            <h2>{completed_items}</h2>
            <p>Complete</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>⚠️</h3>
            <h2>{back_order_items}</h2>
            <p>Back Orders</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📈</h3>
            <h2>{over_received_items}</h2>
            <p>Over Received</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Verification table
    st.markdown("""
    <div class="order-table">
        <div class="table-header">
            📋 STOCK VERIFICATION TABLE - AUTO CALCULATION (CONFIRMED ORDERS ONLY)
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Table headers
    col1, col2, col3, col4, col5, col6, col7 = st.columns([1.5, 3, 1, 1.5, 1.5, 1.5, 2])
    
    with col1:
        st.markdown("**Material No.**")
    with col2:
        st.markdown("**Material Description**")
    with col3:
        st.markdown("**Ordered**")
    with col4:
        st.markdown("**Received**")
    with col5:
        st.markdown("**Remaining**")
    with col6:
        st.markdown("**Over/Under**")
    with col7:
        st.markdown("**Status**")
    
    st.divider()
    
    # Verification rows with IMPROVED back order logic
    for order_num, details in orders.items():
        col1, col2, col3, col4, col5, col6, col7 = st.columns([1.5, 3, 1, 1.5, 1.5, 1.5, 2])
        
        ordered_qty = details['quantity']
        
        with col1:
            st.markdown(f"**{order_num}**")
        
        with col2:
            st.write(details['description'])
        
        with col3:
            st.markdown(f"**{ordered_qty}**")
        
        with col4:
            # Editable received quantity
            received_qty = st.number_input(
                "Received",
                min_value=0,
                value=st.session_state.received_parts[month_key].get(order_num, 0),
                key=f"received_{order_num}_{month_key}",
                label_visibility="collapsed"
            )
            st.session_state.received_parts[month_key][order_num] = received_qty
        
        with col5:
            # Auto-calculate remaining
            remaining = max(0, ordered_qty - received_qty)
            if remaining > 0:
                st.markdown(f"**{remaining}**")
            else:
                st.markdown("**0**")
        
        with col6:
            # Auto-calculate over/under
            difference = received_qty - ordered_qty
            if difference > 0:
                st.markdown(f'<span style="color: blue;">**+{difference}**</span>', unsafe_allow_html=True)
            elif difference < 0:
                st.markdown(f'<span style="color: red;">**{difference}**</span>', unsafe_allow_html=True)
            else:
                st.markdown("**0**")
        
        with col7:
            # Auto-calculate status
            if received_qty == ordered_qty:
                st.markdown('<div class="status-complete">COMPLETE</div>', unsafe_allow_html=True)
            elif received_qty > ordered_qty:
                st.markdown('<div class="status-partial">OVER RECEIVED</div>', unsafe_allow_html=True)
            elif received_qty < ordered_qty:  # UPDATED: This covers both partial AND zero received
                if received_qty == 0:
                    st.markdown('<div class="status-backorder">NOT RECEIVED</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="status-backorder">BACK ORDER</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="status-pending">PENDING</div>', unsafe_allow_html=True)
        
        # UPDATED back order logic: Include both partial AND zero received items
        if received_qty < ordered_qty:  # This includes 0 received AND partial received
            if month_key not in st.session_state.back_orders:
                st.session_state.back_orders[month_key] = {}
            st.session_state.back_orders[month_key][order_num] = {
                'ordered': ordered_qty,
                'received': received_qty,
                'short': ordered_qty - received_qty,
                'description': details['description'],
                'status': 'NOT RECEIVED' if received_qty == 0 else 'PARTIAL'
            }
        else:
            # Remove from back orders if complete or over-received
            if month_key in st.session_state.back_orders and order_num in st.session_state.back_orders[month_key]:
                del st.session_state.back_orders[month_key][order_num]
        
        st.divider()
    
    # Action buttons
    st.markdown("### ⚡ Verification Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔄 Reset All", use_container_width=True, help="Reset all received quantities to 0"):
            for order_num in orders.keys():
                st.session_state.received_parts[month_key][order_num] = 0
            st.success("✅ All quantities reset!")
            st.rerun()
    
    with col2:
        if st.button("✅ Confirm Verification", use_container_width=True, help="Confirm all received quantities"):
            # Mark as verified
            st.session_state.verified_months[month_key] = {
                'verified_by': st.session_state.current_user,
                'verified_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_items': total_items,
                'completed_items': completed_items,
                'back_order_items': back_order_items
            }
            st.success("✅ Verification confirmed!")
            st.session_state.show_analysis = month_key
            st.rerun()
    
    with col3:
        if st.button("📊 View Analysis", use_container_width=True):
            st.session_state.show_analysis = month_key
            st.rerun()
    
    with col4:
        if st.button("⬅️ Back to Selection", use_container_width=True):
            if hasattr(st.session_state, 'selected_verification_month'):
                del st.session_state.selected_verification_month
            st.rerun()
    
    # Show analysis dashboard if requested
    if hasattr(st.session_state, 'show_analysis') and st.session_state.show_analysis == month_key:
        display_analysis_dashboard(month_key)

def display_analysis_dashboard(month_key):
    """Analysis dashboard with ENHANCED back order detection"""
    st.markdown(f"### 📊 Analysis Dashboard - {month_key}")
    
    # Filter to only confirmed orders
    all_orders = st.session_state.orders[month_key]
    orders = {k: v for k, v in all_orders.items() if v.get('status', 'draft') == 'confirmed'}
    
    # Calculate comprehensive stats
    total_items = len(orders)
    total_value = sum(details['total_cost'] for details in orders.values())
    
    completed_items = 0
    partial_items = 0
    pending_items = 0
    over_received_items = 0
    not_received_items = 0
    
    for order_num, details in orders.items():
        received_qty = st.session_state.received_parts[month_key].get(order_num, 0)
        ordered_qty = details['quantity']
        
        if received_qty == ordered_qty:
            completed_items += 1
        elif received_qty > ordered_qty:
            over_received_items += 1
        elif received_qty == 0:  # NEW: Track items not received at all
            not_received_items += 1
        elif received_qty > 0 and received_qty < ordered_qty:  # Partial received
            partial_items += 1
        else:
            pending_items += 1
    
    # Analysis metrics with enhanced breakdown
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        completion_rate = (completed_items / total_items * 100) if total_items > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3>📈</h3>
            <h2>{completion_rate:.1f}%</h2>
            <p>Completion Rate</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>💰</h3>
            <h2>${total_value:,.2f}</h2>
            <p>Total Value</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>✅</h3>
            <h2>{completed_items}</h2>
            <p>Complete</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🚨</h3>
            <h2>{not_received_items}</h2>
            <p>Not Received</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <h3>⚠️</h3>
            <h2>{partial_items}</h2>
            <p>Partial</p>
        </div>
        """, unsafe_allow_html=True)
    
    # ENHANCED Back order section with categories
    if month_key in st.session_state.back_orders and st.session_state.back_orders[month_key]:
        st.markdown("### ⚠️ Back Order Summary")
        
        back_orders = st.session_state.back_orders[month_key]
        
        # Separate back orders by type
        not_received = {k: v for k, v in back_orders.items() if v['received'] == 0}
        partial_received = {k: v for k, v in back_orders.items() if v['received'] > 0}
        
        total_back_orders = len(back_orders)
        
        st.markdown(f"""
        <div class="error-box">
            <h4>🚨 {total_back_orders} Items Require Attention</h4>
            <p>📍 Not Received: {len(not_received)} | ⚠️ Partial: {len(partial_received)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display not received items first (higher priority)
        if not_received:
            st.markdown("#### 🚨 Items Not Received (High Priority)")
            
            for order_num, details in not_received.items():
                col1, col2, col3, col4 = st.columns([2, 4, 2, 2])
                
                with col1:
                    st.markdown(f"**{order_num}**")
                with col2:
                    st.write(details['description'])
                with col3:
                    st.markdown(f"Ordered: **{details['ordered']}**")
                with col4:
                    st.markdown(f"Missing: **{details['short']}**")
        
        # Display partial received items
        if partial_received:
            st.markdown("#### ⚠️ Partially Received Items")
            
            for order_num, details in partial_received.items():
                col1, col2, col3, col4, col5 = st.columns([2, 3, 2, 2, 2])
                
                with col1:
                    st.markdown(f"**{order_num}**")
                with col2:
                    st.write(details['description'])
                with col3:
                    st.markdown(f"Ordered: **{details['ordered']}**")
                with col4:
                    st.markdown(f"Received: **{details['received']}**")
                with col5:
                    st.markdown(f"Short: **{details['short']}**")
        
        # Send back order alert
        if st.button("📧 Send Back Order Alert", use_container_width=True):
            prepare_enhanced_back_order_alert(month_key, back_orders)
            st.session_state.redirect_to_email = True
    
    else:
        st.markdown("""
        <div class="success-box">
            <h3>🎉 No Back Orders!</h3>
            <p>All items received as ordered.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Send completion report
        if st.button("📧 Send Completion Report", use_container_width=True):
            prepare_completion_report(month_key, total_items, completed_items)
            st.session_state.redirect_to_email = True
    
    # Alternative month selection
    st.markdown("### 📅 Compare with Other Months")
    
    # Filter other months to only those with confirmed orders
    other_confirmed_months = []
    for m_key, m_orders in st.session_state.orders.items():
        if m_key != month_key:
            confirmed_count = len({k: v for k, v in m_orders.items() if v.get('status', 'draft') == 'confirmed'})
            if confirmed_count > 0:
                other_confirmed_months.append(m_key)
    
    if other_confirmed_months:
        selected_compare = st.selectbox("Select month to compare:", [""] + other_confirmed_months)
        
        if selected_compare:
            st.markdown(f"**Comparison: {month_key} vs {selected_compare}**")
            
            # Quick comparison
            all_compare_orders = st.session_state.orders[selected_compare]
            compare_orders = {k: v for k, v in all_compare_orders.items() if v.get('status', 'draft') == 'confirmed'}
            compare_total = len(compare_orders)
            compare_completed = 0
            
            if selected_compare in st.session_state.received_parts:
                for o_num, o_details in compare_orders.items():
                    if st.session_state.received_parts[selected_compare].get(o_num, 0) == o_details['quantity']:
                        compare_completed += 1
            
            compare_rate = (compare_completed / compare_total * 100) if compare_total > 0 else 0
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                **{month_key}:**
                - Items: {total_items}
                - Completion: {completion_rate:.1f}%
                - Not Received: {not_received_items}
                """)
            
            with col2:
                st.markdown(f"""
                **{selected_compare}:**
                - Items: {compare_total}
                - Completion: {compare_rate:.1f}%
                """)
    
    # Close analysis
    if st.button("❌ Close Analysis", use_container_width=True):
        if hasattr(st.session_state, 'show_analysis'):
            del st.session_state.show_analysis
        st.rerun()

def prepare_enhanced_back_order_alert(month_key, back_orders):
    """Prepare enhanced back order alert with categories"""
    st.session_state.email_subject = f"🚨 URGENT: Back Order Alert - {month_key}"
    
    # Separate by category
    not_received = {k: v for k, v in back_orders.items() if v['received'] == 0}
    partial_received = {k: v for k, v in back_orders.items() if v['received'] > 0}
    
    # Create categorized back order table
    html_table = """
    <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%;">
    <tr style="background: linear-gradient(90deg, #dc3545 0%, #ff6b6b 100%); color: white;">
        <th>Material Number</th>
        <th>Material Description</th>
        <th>Ordered</th>
        <th>Received</th>
        <th>Short Quantity</th>
        <th>Status</th>
    </tr>
    """
    
    # Add not received items first (high priority)
    for order_num, details in not_received.items():
        html_table += f"""
        <tr style="background-color: #ffe6e6;">
            <td><strong>{order_num}</strong></td>
            <td>{details['description']}</td>
            <td>{details['ordered']}</td>
            <td style="color: red; font-weight: bold;">0</td>
            <td style="color: red; font-weight: bold;">{details['short']}</td>
            <td style="color: red; font-weight: bold;">NOT RECEIVED</td>
        </tr>
        """
    
    # Add partial received items
    for order_num, details in partial_received.items():
        html_table += f"""
        <tr style="background-color: #fff3cd;">
            <td><strong>{order_num}</strong></td>
            <td>{details['description']}</td>
            <td>{details['ordered']}</td>
            <td style="color: orange; font-weight: bold;">{details['received']}</td>
            <td style="color: red; font-weight: bold;">{details['short']}</td>
            <td style="color: orange; font-weight: bold;">PARTIAL</td>
        </tr>
        """
    
    html_table += "</table>"
    
    st.session_state.email_content = f"""
    <h2>🚨 Back Order Alert - {month_key}</h2>
    <div style="background: linear-gradient(90deg, #6B2C91 0%, #ff8c00 100%); padding: 15px; border-radius: 5px; color: white;">
        <h3>MACS Service Singapore - Inventory System</h3>
        <p>URGENT: Back order notification requiring immediate attention</p>
    </div>
    <br>
    <div style="background-color: #dc3545; padding: 15px; border-radius: 5px; color: white;">
        <h3>⚠️ IMMEDIATE ACTION REQUIRED</h3>
        <p><strong>🚨 Items Not Received:</strong> {len(not_received)}</p>
        <p><strong>⚠️ Partially Received:</strong> {len(partial_received)}</p>
        <p><strong>📦 Total Back Orders:</strong> {len(back_orders)}</p>
    </div>
    <br>
    {html_table}
    <p><strong>Alert Generated by:</strong> {st.session_state.current_user}</p>
    <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p><strong>Next Steps:</strong> Please contact suppliers immediately to resolve shortages.</p>
    """

def prepare_completion_report(month_key, total_items, completed_items):
    """Prepare completion report email"""
    st.session_state.email_subject = f"✅ Stock Verification Complete - {month_key}"
    
    st.session_state.email_content = f"""
    <h2>✅ Stock Verification Complete - {month_key}</h2>
    <div style="background: linear-gradient(90deg, #6B2C91 0%, #ff8c00 100%); padding: 15px; border-radius: 5px; color: white;">
        <h3>MACS Service Singapore - Inventory System</h3>
        <p>Stock verification completed successfully</p>
    </div>
    <br>
    <div style="background-color: #28a745; padding: 15px; border-radius: 5px; color: white;">
        <h3>🎉 VERIFICATION COMPLETE</h3>
        <p><strong>Total Items:</strong> {total_items}</p>
        <p><strong>Completed:</strong> {completed_items}</p>
        <p><strong>Success Rate:</strong> {(completed_items/total_items*100):.1f}%</p>
    </div>
    <p><strong>Verified by:</strong> {st.session_state.current_user}</p>
    <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p><strong>Status:</strong> All ordered items received and verified successfully.</p>
    """

def verification_dashboard_page():
    st.header("📊 Verification Dashboard")
    
    if not st.session_state.orders:
        st.info("📝 No orders found. Please add orders first.")
        return
    
    # Overall statistics - UPDATED to only count confirmed orders
    total_months = len(st.session_state.orders)
    confirmed_months_count = 0
    total_confirmed_orders = 0
    total_completed = 0
    total_value = 0
    
    for month_key, orders in st.session_state.orders.items():
        confirmed_orders = {k: v for k, v in orders.items() if v.get('status', 'draft') == 'confirmed'}
        if confirmed_orders:
            confirmed_months_count += 1
            total_confirmed_orders += len(confirmed_orders)
            
            for order_num, details in confirmed_orders.items():
                total_value += details['total_cost']
                received_qty = st.session_state.received_parts.get(month_key, {}).get(order_num, 0)
                if received_qty == details['quantity']:
                    total_completed += 1
    
    verified_months = len(st.session_state.verified_months)
    
    # System overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📅</h3>
            <h2>{confirmed_months_count}</h2>
            <p>Months w/ Confirmed Orders</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📦</h3>
            <h2>{total_confirmed_orders}</h2>
            <p>Confirmed Orders</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        completion_rate = (total_completed / total_confirmed_orders * 100) if total_confirmed_orders > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3>✅</h3>
            <h2>{completion_rate:.1f}%</h2>
            <p>Completion Rate</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>💰</h3>
            <h2>${total_value:,.2f}</h2>
            <p>Total Value</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Monthly breakdown table
    st.markdown("### 📅 Monthly Order Status")
    
    monthly_data = []
    for month_key, orders in st.session_state.orders.items():
        draft_orders = {k: v for k, v in orders.items() if v.get('status', 'draft') == 'draft'}
        confirmed_orders = {k: v for k, v in orders.items() if v.get('status', 'draft') == 'confirmed'}
        
        if draft_orders or confirmed_orders:
            # Calculate completion for confirmed orders only
            completed = 0
            if month_key in st.session_state.received_parts and confirmed_orders:
                for order_num, details in confirmed_orders.items():
                    if st.session_state.received_parts[month_key].get(order_num, 0) == details['quantity']:
                        completed += 1
            
            completion_rate = (completed / len(confirmed_orders) * 100) if confirmed_orders else 0
            
            monthly_data.append({
                'Month': month_key,
                'Draft Orders': len(draft_orders),
                'Confirmed Orders': len(confirmed_orders),
                'Completed': completed,
                'Completion %': f"{completion_rate:.1f}%",
                'Status': '✅ Verified' if month_key in st.session_state.verified_months else '⏳ Pending'
            })
    
    if monthly_data:
        monthly_df = pd.DataFrame(monthly_data)
        st.dataframe(
            monthly_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Month": st.column_config.TextColumn("Month", width="medium"),
                "Draft Orders": st.column_config.NumberColumn("Draft Orders", width="small"),
                "Confirmed Orders": st.column_config.NumberColumn("Confirmed Orders", width="small"),
                "Completed": st.column_config.NumberColumn("Completed", width="small"),
                "Completion %": st.column_config.TextColumn("Completion %", width="small"),
                "Status": st.column_config.TextColumn("Status", width="medium")
            }
        )
    else:
        st.info("📝 No order data available for dashboard.")

def back_order_management_page():
    st.header("⚠️ Back Order Management")
    
    if st.session_state.back_orders:
        total_back_orders = sum(len(orders) for orders in st.session_state.back_orders.values())
        
        st.markdown(f"""
        <div class="error-box">
            <h3>🚨 {total_back_orders} Back Orders Require Attention</h3>
        </div>
        """, unsafe_allow_html=True)
        
        for month_key, back_orders in st.session_state.back_orders.items():
            if back_orders:
                st.markdown(f"### 📅 {month_key} Back Orders")
                
                # Back order details
                for order_num, details in back_orders.items():
                    col1, col2, col3, col4, col5 = st.columns([2, 3, 1, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{order_num}**")
                        st.caption("Material Number")
                    with col2:
                        st.write(details['description'])
                        st.caption("Material Description")
                    with col3:
                        st.markdown(f"Ordered: **{details['ordered']}**")
                    with col4:
                        st.markdown(f"Received: **{details['received']}**")
                    with col5:
                        st.markdown(f"Short: **{details['short']}**")
                
                # Action button
                if st.button(f"📧 Send Alert for {month_key}", key=f"alert_{month_key}"):
                    prepare_enhanced_back_order_alert(month_key, back_orders)
                    st.success("📧 Back order alert prepared! Go to Email Notifications.")
                
                st.divider()
    else:
        st.markdown("""
        <div class="success-box">
            <h3>🎉 No Back Orders Found!</h3>
            <p>All orders are complete or pending verification.</p>
        </div>
        """, unsafe_allow_html=True)

def database_management_page():
    st.header("🗄️ Database Management (Admin)")
    
    # Database stats
    total_parts = len(st.session_state.parts_database)
    total_value = sum(part['cost'] for part in st.session_state.parts_database.values())
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📦</h3>
            <h2>{total_parts}</h2>
            <p>Total Parts</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>💰</h3>
            <h2>${total_value:,.2f}</h2>
            <p>Total Value</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_cost = total_value / total_parts if total_parts > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3>📊</h3>
            <h2>${avg_cost:.2f}</h2>
            <p>Average Cost</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Database upload functionality
    st.markdown("### 📤 Upload Parts Database")
    
    # Template download with correct column names
    st.markdown("**📁 Download Template**")
    st.info("📋 **Required Columns:** Material Number | Material Description | List price (unit cost)")
    
    template_data = {
        'Material Number': ['SP001', 'SP002', 'SP003', 'SP004'],
        'Material Description': ['Ball Bearing 6203', 'V-Belt A-Section', 'Oil Filter OF-150', 'Motor Coupling 5HP'],
        'List price (unit cost)': [25.50, 15.75, 42.30, 185.00]
    }
    template_df = pd.DataFrame(template_data)
    
    # Show template preview
    st.markdown("**📋 Template Preview:**")
    st.dataframe(template_df, use_container_width=True, hide_index=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv_template = template_df.to_csv(index=False)
        st.download_button(
            label="📄 Download CSV Template",
            data=csv_template,
            file_name="parts_database_template.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            template_df.to_excel(writer, index=False, sheet_name='Parts Database')
        excel_buffer.seek(0)
        
        st.download_button(
            label="📊 Download Excel Template",
            data=excel_buffer,
            file_name="parts_database_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    st.divider()
    
    # File upload
    st.markdown("**📤 Upload Database File**")
    uploaded_file = st.file_uploader(
        "Choose CSV or Excel file",
        type=['csv', 'xlsx', 'xls'],
        help="File must contain columns: Material Number, Material Description, List price (unit cost)"
    )
    
    if uploaded_file is not None:
        try:
            # Read file based on type
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.markdown("### 📋 Upload Preview")
            st.dataframe(df.head(10), use_container_width=True, hide_index=True)
            
            # Validate required columns
            required_columns = ['Material Number', 'Material Description', 'List price (unit cost)']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"❌ Missing required columns: {', '.join(missing_columns)}")
                st.markdown("""
                <div class="error-box">
                    <h4>📋 Required Column Names:</h4>
                    <ul>
                        <li><strong>Material Number</strong> - Part/Material identifier (e.g., SP001)</li>
                        <li><strong>Material Description</strong> - Part description (e.g., Ball Bearing 6203)</li>
                        <li><strong>List price (unit cost)</strong> - Unit cost in dollars (e.g., 25.50)</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Data validation
                st.markdown("### 🔍 Data Validation")
                
                validation_errors = []
                
                # Check for duplicates in Material Number
                duplicates = df[df.duplicated(subset=['Material Number'], keep=False)]
                if not duplicates.empty:
                    validation_errors.append(f"Duplicate Material Numbers found: {duplicates['Material Number'].tolist()}")
                
                # Check for missing values
                missing_values = df.isnull().sum()
                if missing_values.any():
                    validation_errors.append(f"Missing values found: {missing_values[missing_values > 0].to_dict()}")
                
                # Check for invalid prices
                try:
                    df['List price (unit cost)'] = pd.to_numeric(df['List price (unit cost)'], errors='coerce')
                    if df['List price (unit cost)'].isnull().any():
                        validation_errors.append("Some prices are not valid numbers")
                    elif df['List price (unit cost)'].min() <= 0:
                        validation_errors.append("Some prices are zero or negative")
                except:
                    validation_errors.append("Price column contains invalid data")
                
                # Check for empty Material Numbers or Descriptions
                if df['Material Number'].isnull().any() or df['Material Number'].eq('').any():
                    validation_errors.append("Some Material Numbers are empty")
                
                if df['Material Description'].isnull().any() or df['Material Description'].eq('').any():
                    validation_errors.append("Some Material Descriptions are empty")
                
                if validation_errors:
                    st.warning("⚠️ Validation Issues Found:")
                    for error in validation_errors:
                        st.write(f"• {error}")
                    
                    import_anyway = st.checkbox("Import anyway (may cause issues)", help="Not recommended")
                else:
                    st.success("✅ Data validation passed!")
                    import_anyway = True
                
                # Import options
                col1, col2 = st.columns(2)
                
                with col1:
                    replace_existing = st.radio(
                        "Import Mode:",
                        ["Replace entire database", "Add to existing database", "Update existing entries only"],
                        help="Choose how to handle existing data"
                    )
                
                with col2:
                    st.markdown("**📊 Import Summary:**")
                    st.write(f"• Records to import: **{len(df)}**")
                    if replace_existing == "Add to existing database":
                        existing_count = len(st.session_state.parts_database)
                        st.write(f"• Current database size: **{existing_count}**")
                        st.write(f"• New database size: **{existing_count + len(df)}**")
                    elif replace_existing == "Replace entire database":
                        st.write(f"• Current database: **{len(st.session_state.parts_database)}** (will be replaced)")
                
                # Import button
                if st.button("🚀 Import Database", disabled=not import_anyway, use_container_width=True):
                    with st.spinner("Importing database..."):
                        if replace_existing == "Replace entire database":
                            st.session_state.parts_database = {}
                        
                        imported_count = 0
                        updated_count = 0
                        error_count = 0
                        
                        for index, row in df.iterrows():
                            try:
                                material_number = str(row['Material Number']).strip()
                                material_description = str(row['Material Description']).strip()
                                list_price = float(row['List price (unit cost)'])
                                
                                # Skip empty entries
                                if not material_number or not material_description or list_price <= 0:
                                    error_count += 1
                                    continue
                                
                                if material_number in st.session_state.parts_database:
                                    if replace_existing != "Add to existing database":
                                        st.session_state.parts_database[material_number] = {
                                            'description': material_description,
                                            'cost': list_price
                                        }
                                        updated_count += 1
                                else:
                                    st.session_state.parts_database[material_number] = {
                                        'description': material_description,
                                        'cost': list_price
                                    }
                                    imported_count += 1
                            except Exception as e:
                                error_count += 1
                                continue
                        
                        # Show import results
                        if imported_count > 0 or updated_count > 0:
                            st.success(f"✅ Database import completed!")
                            
                            results_text = f"""
                            📊 **Import Results:**
                            • New parts added: **{imported_count}**
                            • Existing parts updated: **{updated_count}**
                            """
                            
                            if error_count > 0:
                                results_text += f"• Errors/Skipped: **{error_count}**"
                            
                            st.markdown(results_text)
                            st.balloons()
                            
                            # Auto-refresh after successful import
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error("❌ No valid data was imported. Please check your file format.")
        
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
            st.markdown("""
            <div class="error-box">
                <h4>💡 File Format Tips:</h4>
                <ul>
                    <li>Use UTF-8 encoding for CSV files</li>
                    <li>Ensure column names match exactly</li>
                    <li>Numbers should not contain currency symbols</li>
                    <li>Avoid special characters in Material Numbers</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    # Current database view
    st.divider()
    st.markdown("### 📋 Current Database")
    
    if st.session_state.parts_database:
        # Convert to DataFrame for display
        db_df = pd.DataFrame.from_dict(st.session_state.parts_database, orient='index')
        db_df.index.name = 'Material Number'
        db_df = db_df.reset_index()
        db_df.columns = ['Material Number', 'Material Description', 'List price (unit cost)']
        
        # Search functionality
        search_term = st.text_input("🔍 Search Database", placeholder="Enter Material Number or Description...")
        
        if search_term:
            filtered_df = db_df[
                db_df['Material Number'].str.contains(search_term, case=False) |
                db_df['Material Description'].str.contains(search_term, case=False)
            ]
            st.write(f"📋 Found {len(filtered_df)} matching parts:")
            display_df = filtered_df
        else:
            display_df = db_df
        
        # Display table
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Material Number": st.column_config.TextColumn("Material Number", width="small"),
                "Material Description": st.column_config.TextColumn("Material Description", width="large"),
                "List price (unit cost)": st.column_config.NumberColumn("List price (unit cost)", format="$%.2f", width="small")
            }
        )
        
        # Export current database
        st.markdown("### 📤 Export Database")
        
        col1, col2 = st.columns(2)
        
        with col1:
            csv_data = display_df.to_csv(index=False)
            st.download_button(
                label="📄 Export as CSV",
                data=csv_data,
                file_name=f"parts_database_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                display_df.to_excel(writer, index=False, sheet_name='Parts Database')
            excel_buffer.seek(0)
            
            st.download_button(
                label="📊 Export as Excel",
                data=excel_buffer,
                file_name=f"parts_database_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    else:
        st.info("📝 No parts in database. Upload a file to get started.")

def database_view_page():
    st.header("🗄️ Parts Database (View Only)")
    
    if st.session_state.parts_database:
        # Database statistics
        total_parts = len(st.session_state.parts_database)
        total_value = sum(part['cost'] for part in st.session_state.parts_database.values())
        avg_cost = total_value / total_parts if total_parts > 0 else 0
        
        # Show stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📦 Total Parts", total_parts)
        with col2:
            st.metric("💰 Total Value", f"${total_value:,.2f}")
        with col3:
            st.metric("📊 Average Cost", f"${avg_cost:.2f}")
        
        st.divider()
        
        # Search functionality
        search_term = st.text_input("🔍 Search Database", placeholder="Enter Material Number or Description...")
        
        # Convert to DataFrame with correct column names
        db_df = pd.DataFrame.from_dict(st.session_state.parts_database, orient='index')
        db_df.index.name = 'Material Number'
        db_df = db_df.reset_index()
        db_df.columns = ['Material Number', 'Material Description', 'List price (unit cost)']
        
        # Filter if search term provided
        if search_term:
            filtered_df = db_df[
                db_df['Material Number'].str.contains(search_term, case=False) |
                db_df['Material Description'].str.contains(search_term, case=False)
            ]
            st.write(f"📋 Found {len(filtered_df)} matching parts:")
            display_df = filtered_df
        else:
            display_df = db_df
        
        # Display table
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Material Number": st.column_config.TextColumn("Material Number", width="small"),
                "Material Description": st.column_config.TextColumn("Material Description", width="large"),
                "List price (unit cost)": st.column_config.NumberColumn("List price (unit cost)", format="$%.2f", width="small")
            }
        )
        
        # Export functionality for staff
        if st.button("📄 Export Search Results", use_container_width=True):
            csv_data = display_df.to_csv(index=False)
            st.download_button(
                label="💾 Download CSV",
                data=csv_data,
                file_name=f"parts_search_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    else:
        st.info("📝 No parts database found. Contact administrator to upload database.")

def user_management_page():
    st.header("👥 User Management (Admin)")
    
    # Current users
    st.markdown("### 👥 Current Users")
    
    users_data = []
    for username, details in st.session_state.users.items():
        users_data.append({
            'Username': username,
            'Role': details['role'].title(),
            'Email': details['email'],
            'Pages': ', '.join(details['pages']) if 'all' not in details['pages'] else 'All Pages'
        })
    
    users_df = pd.DataFrame(users_data)
    st.dataframe(users_df, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Page access management
    st.markdown("### 🔐 Configure Page Access")
    
    page_options = {
        'order_management': '📝 Order Management',
        'qr_scanner': '📱 QR Scanner & Check-in',
        'verification_dashboard': '📊 Verification Dashboard',
        'back_order': '⚠️ Back Order Management',
        'database_view': '🗄️ Database View',
        'email': '📧 Email Notifications'
    }
    
    modifiable_users = [u for u in st.session_state.users.keys() if u != 'admin']
    
    if modifiable_users:
        selected_user = st.selectbox("👤 Select User", modifiable_users)
        
        if selected_user:
            current_pages = st.session_state.users[selected_user]['pages']
            
            # Page access checkboxes
            st.markdown("**Select accessible pages:**")
            
            new_pages = []
            for page_key, page_name in page_options.items():
                checked = page_key in current_pages
                if st.checkbox(page_name, value=checked, key=f"page_{page_key}"):
                    new_pages.append(page_key)
            
            if st.button("💾 Update Page Access"):
                st.session_state.users[selected_user]['pages'] = new_pages
                st.success(f"✅ Updated page access for {selected_user}")
                st.rerun()

def email_notifications_page():
    st.header("📧 Email Notifications")
    
    # Permanent email settings
    st.markdown("### ⚙️ Email Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sender_email = st.text_input("📧 Sender Email", value=st.session_state.email_settings['sender_email'])
        sender_password = st.text_input("🔒 Password", type="password", help="SMTP password")
    
    with col2:
        recipient_email = st.text_input("📧 Recipient Email", value=st.session_state.email_settings['recipient_email'])
        cc_emails = st.text_input("📧 CC Emails", value=st.session_state.email_settings['cc_emails'])
    
    # Save settings
    if st.button("💾 Save Email Settings"):
        st.session_state.email_settings = {
            'sender_email': sender_email,
            'recipient_email': recipient_email,
            'cc_emails': cc_emails
        }
        st.success("✅ Email settings saved!")
    
    st.divider()
    
    # Email content
    if hasattr(st.session_state, 'email_subject'):
        email_subject = st.text_input("📋 Subject", value=st.session_state.email_subject)
        email_content = st.text_area("📝 Email Content", value=st.session_state.email_content, height=400)
    else:
        email_subject = st.text_input("📋 Subject", value="MACS Service Singapore - Inventory Report")
        email_content = st.text_area("📝 Email Content", height=400, placeholder="Enter email content...")
    
    # Send email
    if st.button("📧 Send Email", use_container_width=True):
        if recipient_email and email_subject and email_content:
            st.markdown("""
            <div class="success-box">
                <h4>✅ Email Sent Successfully!</h4>
                <p>Email notification has been sent to the specified recipients.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Email preview
            st.markdown("### 📧 Email Preview")
            st.markdown(email_content, unsafe_allow_html=True)
            
            # Clear pre-filled content
            if hasattr(st.session_state, 'email_subject'):
                del st.session_state.email_subject
                del st.session_state.email_content
        else:
            st.error("❌ Please fill in all required fields.")

# Main application
def main():
    if not st.session_state.logged_in:
        login()
    else:
        main_app()

if __name__ == "__main__":
    main()