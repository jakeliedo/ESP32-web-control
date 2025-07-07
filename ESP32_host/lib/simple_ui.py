"""
Simple UI Library for WC Remote Control
Provides basic UI components for the remote control interface
"""

from lib.st7789p3 import ST7789P3

class SimpleUI:
    """Simple UI Manager for WC Remote Control"""
    
    def __init__(self, display):
        """Initialize UI with display"""
        self.display = display
        self.width = display.WIDTH
        self.height = display.HEIGHT
        
        # UI Configuration
        self.header_height = 40
        self.footer_height = 30
        self.node_height = 50
        self.margin = 10
        
        # Colors
        self.bg_color = ST7789P3.BLACK
        self.header_color = ST7789P3.BLUE
        self.text_color = ST7789P3.WHITE
        self.selected_color = ST7789P3.YELLOW
        self.online_color = ST7789P3.GREEN
        self.offline_color = ST7789P3.RED
        self.border_color = ST7789P3.GRAY
        
    def clear_screen(self):
        """Clear entire screen"""
        self.display.fill(self.bg_color)
    
    def draw_header(self, title="WC Remote Control"):
        """Draw header bar"""
        # Header background
        self.display.rect(0, 0, self.width, self.header_height, self.header_color, fill=True)
        
        # Header text
        text_x = (self.width - len(title) * 8) // 2
        text_y = (self.header_height - 8) // 2
        self.display.text(title, text_x, text_y, self.text_color, self.header_color)
        
        # Header border
        self.display.hline(0, self.header_height - 1, self.width, self.border_color)
    
    def draw_footer(self, wifi_status, mqtt_status):
        """Draw footer with connection status"""
        footer_y = self.height - self.footer_height
        
        # Footer background
        self.display.rect(0, footer_y, self.width, self.footer_height, self.bg_color, fill=True)
        
        # WiFi status
        wifi_color = self.online_color if wifi_status else self.offline_color
        wifi_text = "WiFi:ON" if wifi_status else "WiFi:OFF"
        self.display.text(wifi_text, 5, footer_y + 5, wifi_color)
        
        # MQTT status
        mqtt_color = self.online_color if mqtt_status else self.offline_color
        mqtt_text = "MQTT:ON" if mqtt_status else "MQTT:OFF"
        self.display.text(mqtt_text, 80, footer_y + 5, mqtt_color)
        
        # Time (placeholder)
        time_text = "12:34"
        time_x = self.width - len(time_text) * 8 - 5
        self.display.text(time_text, time_x, footer_y + 5, self.text_color)
        
        # Footer border
        self.display.hline(0, footer_y, self.width, self.border_color)
    
    def draw_node_list(self, nodes, selected_index, node_status=None):
        """Draw list of WC nodes with status"""
        start_y = self.header_height + self.margin
        content_height = self.height - self.header_height - self.footer_height - 2 * self.margin
        
        # Clear content area
        self.display.rect(0, start_y, self.width, content_height, self.bg_color, fill=True)
        
        # Draw nodes
        for i, node in enumerate(nodes):
            if i >= 4:  # Maximum 4 nodes
                break
                
            node_y = start_y + i * self.node_height
            node_name = node.get('name', f'Node {i+1}')
            
            # Get node status
            if node_status and node['id'] in node_status:
                status = node_status[node['id']]['status']
            else:
                status = 'offline'
            
            # Determine node type from ID
            if 'male' in node['id']:
                node_type = 'male'
            elif 'female' in node['id']:
                node_type = 'female'
            else:
                node_type = 'unknown'
            
            # Node background
            if i == selected_index:
                # Highlight selected node
                self.display.rect(self.margin, node_y, 
                                self.width - 2 * self.margin, self.node_height - 5, 
                                self.selected_color, fill=True)
                text_color = self.bg_color
            else:
                # Normal node background
                self.display.rect(self.margin, node_y, 
                                self.width - 2 * self.margin, self.node_height - 5, 
                                self.border_color)
                text_color = self.text_color
            
            # Node icon (M/F indicator)
            icon_x = self.margin + 5
            icon_y = node_y + 5
            icon_text = "M" if node_type == "male" else "F"
            icon_color = ST7789P3.BLUE if node_type == "male" else ST7789P3.MAGENTA
            
            # Draw icon background
            self.display.rect(icon_x, icon_y, 20, 20, icon_color, fill=True)
            self.display.text(icon_text, icon_x + 6, icon_y + 6, self.text_color, icon_color)
            
            # Node name
            name_x = icon_x + 30
            name_y = icon_y
            self.display.text(node_name, name_x, name_y, text_color)
            
            # Status indicator
            status_x = self.width - self.margin - 60
            status_y = icon_y
            status_color = self.online_color if status == "online" else self.offline_color
            status_text = "ON" if status == "online" else "OFF"
            
            # Draw status background
            status_bg_width = len(status_text) * 8 + 4
            self.display.rect(status_x - 2, status_y - 2, 
                            status_bg_width, 12, status_color, fill=True)
            self.display.text(status_text, status_x, status_y, self.text_color, status_color)
            
            # Selection indicator
            if i == selected_index:
                # Draw arrow
                arrow_x = self.margin - 8
                arrow_y = node_y + self.node_height // 2 - 4
                self.display.text(">", arrow_x, arrow_y, self.selected_color)

    def show_message(self, message, duration_ms=2000):
        """Show temporary message overlay"""
        # Clear screen
        self.clear_screen()
        
        # Message background
        msg_width = max(120, len(message) * 8 + 20)
        msg_height = 40
        msg_x = (self.width - msg_width) // 2
        msg_y = (self.height - msg_height) // 2
        
        # Draw message box
        self.display.rect(msg_x, msg_y, msg_width, msg_height, self.header_color, fill=True)
        self.display.rect(msg_x, msg_y, msg_width, msg_height, self.text_color)
        
        # Draw message text
        text_x = msg_x + (msg_width - len(message) * 8) // 2
        text_y = msg_y + (msg_height - 8) // 2
        self.display.text(message, text_x, text_y, self.text_color, self.header_color)
        
        # Automatically clear after duration (blocking)
        if duration_ms > 0:
            import time
            time.sleep(duration_ms / 1000.0)
    
    def draw_splash_screen(self):
        """Draw startup splash screen"""
        self.clear_screen()
        
        # Title
        title = "WC Remote"
        title_x = (self.width - len(title) * 16) // 2
        title_y = 60
        # Draw title larger (simulate with multiple draws)
        for dx in range(2):
            for dy in range(2):
                self.display.text(title, title_x + dx, title_y + dy, self.text_color)
        
        # Version
        version = "v1.0.0"
        version_x = (self.width - len(version) * 8) // 2
        version_y = title_y + 40
        self.display.text(version, version_x, version_y, self.border_color)
        
        # Logo placeholder
        logo_size = 40
        logo_x = (self.width - logo_size) // 2
        logo_y = 140
        self.display.rect(logo_x, logo_y, logo_size, logo_size, self.header_color, fill=True)
        self.display.text("WC", logo_x + 12, logo_y + 16, self.text_color, self.header_color)
        
        # Loading text
        loading_text = "Initializing..."
        loading_x = (self.width - len(loading_text) * 8) // 2
        loading_y = 220
        self.display.text(loading_text, loading_x, loading_y, self.text_color)
    
    def draw_connection_screen(self, status_text):
        """Draw connection status screen"""
        self.clear_screen()
        
        # Connection icon
        icon_size = 30
        icon_x = (self.width - icon_size) // 2
        icon_y = 80
        self.display.rect(icon_x, icon_y, icon_size, icon_size, self.header_color, fill=True)
        self.display.text("NET", icon_x + 3, icon_y + 11, self.text_color, self.header_color)
        
        # Status text
        status_x = (self.width - len(status_text) * 8) // 2
        status_y = 140
        self.display.text(status_text, status_x, status_y, self.text_color)
        
        # Progress dots
        dots = "..."
        dots_x = (self.width - len(dots) * 8) // 2
        dots_y = 170
        self.display.text(dots, dots_x, dots_y, self.border_color)
    
    def draw_error_screen(self, error_text):
        """Draw error screen"""
        self.clear_screen()
        
        # Error icon
        icon_size = 30
        icon_x = (self.width - icon_size) // 2
        icon_y = 80
        self.display.rect(icon_x, icon_y, icon_size, icon_size, self.offline_color, fill=True)
        self.display.text("ERR", icon_x + 3, icon_y + 11, self.text_color, self.offline_color)
        
        # Error text
        error_x = (self.width - len(error_text) * 8) // 2
        error_y = 140
        self.display.text(error_text, error_x, error_y, self.offline_color)
        
        # Retry instruction
        retry_text = "Press SELECT to retry"
        retry_x = (self.width - len(retry_text) * 8) // 2
        retry_y = 200
        self.display.text(retry_text, retry_x, retry_y, self.text_color)
    
    def draw_full_ui(self, nodes, selected_index, wifi_status, mqtt_status):
        """Draw complete UI"""
        self.clear_screen()
        self.draw_header()
        self.draw_node_list(nodes, selected_index)
        self.draw_footer(wifi_status, mqtt_status)
    
    def draw_sending_command(self, node_name):
        """Draw command sending feedback"""
        # Draw overlay
        overlay_width = 180
        overlay_height = 60
        overlay_x = (self.width - overlay_width) // 2
        overlay_y = (self.height - overlay_height) // 2
        
        # Background
        self.display.rect(overlay_x, overlay_y, overlay_width, overlay_height, 
                         self.header_color, fill=True)
        self.display.rect(overlay_x, overlay_y, overlay_width, overlay_height, 
                         self.text_color)
        
        # Text
        text1 = "Sending command"
        text1_x = overlay_x + (overlay_width - len(text1) * 8) // 2
        text1_y = overlay_y + 15
        self.display.text(text1, text1_x, text1_y, self.text_color, self.header_color)
        
        text2 = f"to {node_name}"
        text2_x = overlay_x + (overlay_width - len(text2) * 8) // 2
        text2_y = overlay_y + 35
        self.display.text(text2, text2_x, text2_y, self.text_color, self.header_color)
