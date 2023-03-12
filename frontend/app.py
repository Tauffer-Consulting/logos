from dash import Dash, dcc, html, Input, Output, State, ctx, no_update
import dash_bootstrap_components as dbc
from utils import parse_pdf


app = Dash(__name__, external_stylesheets=[dbc.themes.LITERA])
server=app.server

GRAY = '#474747'

title_image = html.Img(
    src='/assets/images/logos.png', 
    style={'width': '300px', 'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto'}
)

navigate_question = html.Button(
    'Question',
    id='navigate-question',
    style={
        'width': '200px', 
        'display': 'block', 
        'margin-left': 'auto', 
        'margin-right': 'auto',
        'margin-top': '8px',
        'color': GRAY, 
        'background-color': 'white',
        'border-color': 'white', 'border-width': '0px',
        'font-size': '1.3rem', 'line-height': '1.5', 'font-weight': '700',
    }
)

navigate_add = html.Button(
    'Add Document',
    id='navigate-add',
    style={
        'width': '200px', 
        'display': 'block', 
        'margin-left': 'auto', 
        'margin-right': 'auto',
        'margin-top': '8px',
        'color': GRAY, 
        'background-color': 'white',
        'border-color': 'white', 'border-width': '0px',
        'font-size': '1.3rem', 'line-height': '1.5', 'font-weight': '700',
    }
)

first_row = dbc.Row(
    [
        dbc.Col(navigate_question, width={"size": 2, "offset": 4}),
        dbc.Col(navigate_add, width=2),
    ],
    style={
        'margin-top': '10px',
    }
)

# Question components
text_input = dbc.Input(
    id="input", 
    placeholder="Question something...", 
    type="text",
    style={
        'width': '600px', 
        'display': 'block', 
        'margin-left': 'auto', 
        'margin-right': 'auto', 
        'border-color': GRAY,
        'box-shadow': '0px 3px 4px rgb(0 0 0 / 70%)',
    }
)

question_button = dbc.Button(
    "Question", 
    id="button-question", 
    color="primary", 
    style={
        'width': '120px', 
        'display': 'block', 
        'margin-left': 'auto', 
        'margin-right': 'auto',
        'margin-top': '8px',
        'color': GRAY, 
        'background-color': 'white',
        'border-color': GRAY, 'border-radius': '0.25rem', 'border-width': '2px',
        'font-size': '1.1rem', 'line-height': '1.5', 'font-weight': '400',
    }
)

question_component = html.Div(
    children=[
        text_input,
        question_button,
        html.Div(id="output"),
    ],
    id='div-question-component',
)

# Add components
upload_area = dcc.Upload(
    id='upload-data',
    children=html.Div([
        'Drag and Drop or ',
        html.A('Select File')
    ]),
    style={
        'width': '500px',
        'display': 'block', 
        'margin-left': 'auto', 
        'margin-right': 'auto',
        'margin-top': '8px',
        'lineHeight': '60px',
        'borderWidth': '1px',
        'borderStyle': 'dashed',
        'borderRadius': '5px',
        'textAlign': 'center'
    },
    multiple=False
)

title_input = dbc.Row(
    [
        dbc.Label("Title", html_for="input-title-row", width=2),
        dbc.Col(
            dbc.Input(
                type="text", id="input-title-row", placeholder="Title"
            ),
            width=10,
        ),
    ],
    className="mb-3",
)

author_input = dbc.Row(
    [
        dbc.Label("Author", html_for="input-author-row", width=2),
        dbc.Col(
            dbc.Input(
                type="text",
                id="input-author-row",
                placeholder="Author name",
            ),
            width=10,
        ),
    ],
    className="mb-3",
)

year_input = dbc.Row(
    [
        dbc.Label("Year", html_for="input-year-row", width=2),
        dbc.Col(
            dbc.Input(
                type="number", min=-1000, max=2023, step=1,
                id="input-year-row",
                placeholder="2000",
            ),
            width=10,
        ),
    ],
    className="mb-3",
)

add_form = dbc.Form(
    children=[
        title_input, 
        author_input, 
        year_input,
    ],
    style={
        'width': '500px',
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-top': '8px',
    }
)

add_document_button = dbc.Button(
    "Add document", 
    id="button-question", 
    color="primary", 
    style={
        'width': '170px', 
        'display': 'block', 
        'margin-left': 'auto', 
        'margin-right': 'auto',
        'margin-top': '8px',
        'color': GRAY, 
        'background-color': 'white',
        'border-color': GRAY, 'border-radius': '0.25rem', 'border-width': '2px',
        'font-size': '1.1rem', 'line-height': '1.5', 'font-weight': '400',
    }
)

add_component = html.Div(
    children=[
        upload_area,
        html.Br(),
        add_form,
        add_document_button,
    ],
    id='div-add-component',
)

# App layout
app.layout = html.Div(
    children=[
        title_image,
        first_row,
        html.Br(),
        html.Br(),
        html.Div(
            id='div-page-content',
            children=[add_component],
        )
    ]
)


@app.callback(
    Output('div-page-content', 'children'),
    Input('navigate-question', 'n_clicks'),
    Input('navigate-add', 'n_clicks'),
    State('div-page-content', 'children'),
)
def display_page(n_clicks_question, n_clicks_add, page_content):
    button_id = ctx.triggered_id
    if button_id is None:
        return no_update
    elif button_id == 'navigate-question':
        return question_component
    elif button_id == 'navigate-add':
        return add_component


@app.callback(
    Output('input-title-row', 'value'),
    Output('input-author-row', 'value'),
    Output('input-year-row', 'value'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    State('upload-data', 'last_modified')
)
def update_output(file_contents, file_name, last_modified):
    if file_contents is not None:    
        metadata = parse_pdf(base64_pdf_bytestring=file_contents)
        return metadata['title'], metadata['author'], metadata['year']
    return "", "", ""


if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_silence_routes_logging=False)