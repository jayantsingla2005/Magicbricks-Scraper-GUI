import plotly.graph_objects as go
import pandas as pd

# Data for the workflow steps
data = {
    "steps": [
        {"step": 1, "action": "Initialize Chrome WebDriver", "description": "Setup Selenium with headless Chrome browser"},
        {"step": 2, "action": "Load MagicBricks URL", "description": "Navigate to property listings page"},
        {"step": 3, "action": "Parse HTML", "description": "Use BeautifulSoup to parse page content"},
        {"step": 4, "action": "Extract Property Data", "description": "Get title, price, area, bedrooms, bathrooms, images, URLs"},
        {"step": 5, "action": "Check Pagination", "description": "Look for next page link"},
        {"step": 6, "action": "Continue or Finish", "description": "If more pages exist, go to next page, else finish"},
        {"step": 7, "action": "Save to CSV", "description": "Export all scraped data to CSV file"}
    ]
}

# Create DataFrame
df = pd.DataFrame(data["steps"])

# Abbreviate actions to fit 15 character limit
df['short_action'] = [
    'Init WebDriver',
    'Load URL', 
    'Parse HTML',
    'Extract Data',
    'Check Pages',
    'Continue/Finish',
    'Save CSV'
]

# Create figure
fig = go.Figure()

# Define positions for flowchart layout
positions = [
    (2, 6),  # Step 1: Init WebDriver
    (2, 5),  # Step 2: Load URL
    (2, 4),  # Step 3: Parse HTML
    (2, 3),  # Step 4: Extract Data
    (2, 2),  # Step 5: Check Pages
    (2, 1),  # Step 6: Continue/Finish (decision)
    (2, 0)   # Step 7: Save CSV
]

box_width = 1.2
box_height = 0.4

# Colors for each step
colors = ['#1FB8CD', '#DB4545', '#2E8B57', '#5D878F', '#D2BA4C', '#B4413C', '#964325']

# Add boxes for each step
for i, (step_data, pos, color) in enumerate(zip(df.iterrows(), positions, colors)):
    x, y = pos
    step_info = step_data[1]
    
    # Create rectangle shape for box
    if i == 5:  # Decision diamond for step 6
        fig.add_shape(
            type="path",
            path=f"M {x},{y+box_height/2} L {x+box_width/2},{y+box_height} L {x},{y+box_height/2} L {x+box_width/2},{y} L {x},{y-box_height/2} L {x-box_width/2},{y} Z",
            fillcolor=color,
            line=dict(color="#13343B", width=2)
        )
    else:
        fig.add_shape(
            type="rect",
            x0=x-box_width/2, y0=y-box_height/2,
            x1=x+box_width/2, y1=y+box_height/2,
            fillcolor=color,
            line=dict(color="#13343B", width=2)
        )
    
    # Add text label
    fig.add_annotation(
        x=x, y=y,
        text=step_info['short_action'],
        showarrow=False,
        font=dict(color="white", size=12),
        xanchor="center", yanchor="middle"
    )

# Add arrows between steps
arrow_props = dict(
    arrowhead=2,
    arrowsize=1,
    arrowwidth=2,
    arrowcolor="#13343B"
)

# Vertical arrows (1->2->3->4->5->6->7)
for i in range(len(positions)-1):
    if i == 5:  # Skip arrow from step 6 to 7, we'll add it separately
        continue
    x1, y1 = positions[i]
    x2, y2 = positions[i+1]
    
    fig.add_annotation(
        x=x2, y=y2 + box_height/2 + 0.1,
        ax=x1, ay=y1 - box_height/2 - 0.1,
        xref="x", yref="y",
        axref="x", ayref="y",
        showarrow=True,
        **arrow_props
    )

# Arrow from step 6 to step 7 (finish path)
fig.add_annotation(
    x=positions[6][0], y=positions[6][1] + box_height/2 + 0.1,
    ax=positions[5][0], ay=positions[5][1] - box_height/2 - 0.1,
    xref="x", yref="y",
    axref="x", ayref="y",
    showarrow=True,
    **arrow_props
)

# Loop back arrow from step 6 to step 2 (continue path)
fig.add_annotation(
    x=0.8, y=5,
    ax=1.2, ay=1,
    xref="x", yref="y",
    axref="x", ayref="y",
    showarrow=True,
    **arrow_props
)

# Add "More pages" and "Done" labels
fig.add_annotation(
    x=0.5, y=3,
    text="More pages",
    showarrow=False,
    font=dict(color="#13343B", size=10),
    xanchor="center", yanchor="middle"
)

fig.add_annotation(
    x=2.8, y=0.5,
    text="Done",
    showarrow=False,
    font=dict(color="#13343B", size=10),
    xanchor="center", yanchor="middle"
)

# Update layout
fig.update_layout(
    title='MagicBricks Scraper Workflow',
    xaxis=dict(
        range=[-0.5, 4.5],
        showgrid=False,
        showticklabels=False,
        zeroline=False
    ),
    yaxis=dict(
        range=[-0.8, 6.8],
        showgrid=False,
        showticklabels=False,
        zeroline=False
    ),
    plot_bgcolor='white',
    showlegend=False
)

# Save the chart
# Always write interactive HTML (works without extra deps)
fig.write_html('magicbricks_workflow.html', include_plotlyjs='cdn')

# Optional static PNG export if 'kaleido' is available
try:
    import kaleido  # noqa: F401
    fig.write_image('magicbricks_workflow.png')
except Exception as e:
    print(f"[info] PNG export skipped. Install 'kaleido' to enable static image export. Reason: {e}")