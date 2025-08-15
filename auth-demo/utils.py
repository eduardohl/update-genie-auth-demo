from dash import dash_table
from dash_iconify import DashIconify
import dash_mantine_components as dmc


def get_icon(icon):
    return DashIconify(icon=icon, height=16)


def create_data_table(id):
    return dash_table.DataTable(
        id=id,
        style_table={"marginTop": "20px", "width": "100%", "overflowX": "auto"},
        style_header={
            "backgroundColor": "#EEEDE9",
            "fontWeight": "bold",
            "fontFamily": "DM Sans, sans-serif",
            "border": "1px solid #DCDCDC",
        },
        style_cell={
            "textAlign": "left",
            "padding": "10px",
            "fontFamily": "DM Sans, sans-serif",
            "minWidth": "100px",
            "width": "150px",
            "maxWidth": "300px",
            "overflow": "hidden",
            "textOverflow": "ellipsis",
            "border": "1px solid #DCDCDC",
        },
        style_data={
            "whiteSpace": "normal",
            "height": "auto",
            "backgroundColor": "#FFFFFF",
        },
        style_data_conditional=[
            {
                "if": {"row_index": "odd"},
                "backgroundColor": "#F9F7F4",
            }
        ],
        page_size=10,
        sort_action="native",
        filter_action="native",
        tooltip_delay=0,
        tooltip_duration=None,
        tooltip_data=[
            {
                column: {"value": str(value), "type": "markdown"}
                for column, value in row.items()
            }
            for row in [{}]
        ],
        virtualization=True,
        fixed_rows={"headers": True},
    )


def create_genie_list(items, title_key="title", id_key="id"):
    """Create a formatted list for Genie spaces or conversations"""
    if not items:
        return dmc.Text("No items found", size="sm", c="dimmed")
    
    list_items = []
    for item in items:
        # Try different possible key names for ID
        item_id = item.get(id_key) or item.get('space_id') or item.get('_id') or item.get('genie_space_id') or 'Unknown'
        item_title = item.get(title_key) or item.get('name') or item.get('display_name') or 'Untitled'
        
        list_items.append(
            dmc.ListItem([
                dmc.Text(item_title, fw=500),  # Use fw instead of weight
                dmc.Text(f"ID: {item_id}", size="xs", c="dimmed")
            ])
        )
    
    return dmc.List(list_items, size="sm", spacing="xs")


def create_genie_messages_list(messages):
    """Create a formatted list for Genie messages"""
    if not messages:
        return dmc.Text("No messages found", size="sm", c="dimmed")
    
    list_items = []
    for message in messages:
        # Extract message details
        message_id = message.get('id') or message.get('message_id') or message.get('_id') or 'Unknown'
        message_content = message.get('content') or message.get('text') or message.get('message') or 'No content'
        message_role = message.get('role') or message.get('type') or message.get('sender') or 'Unknown'
        message_timestamp = message.get('timestamp') or message.get('created_at') or message.get('time') or 'Unknown'
        
        # Create a card-like display for each message
        message_card = dmc.Paper([
            dmc.Group([
                dmc.Badge(message_role, color="blue", size="sm"),
                dmc.Text(f"ID: {message_id}", size="xs", c="dimmed"),
                dmc.Text(message_timestamp, size="xs", c="dimmed"),
            ], position="apart", mb="xs"),
            dmc.Text(message_content, size="sm", style={"whiteSpace": "pre-wrap"})
        ], p="md", radius="sm", withBorder=True, mb="xs")
        
        list_items.append(message_card)
    
    return dmc.Stack(list_items, spacing="md")
