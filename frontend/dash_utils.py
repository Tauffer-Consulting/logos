from dash import dcc, html
import dash_bootstrap_components as dbc


def create_references_cards(references: list):
    n_rows = len(references) // 3 + 1
    all_rows = list()
    ii = 0
    for row in range(n_rows):
        children = list()
        for col in range(3):
            if ii >= len(references):
                break
            ref = references[ii]
            children.append(
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(f"{ref.payload.get('author')}, {ref.payload.get('title')}, {ref.payload.get('year')}"),
                            dbc.CardBody([html.P(ref.payload.get('text'), className="card-text")]),
                        ]
                    ),
                    width=4,
                )
            )
            ii += 1
        all_rows.append(
            dbc.Row(
                children=children,
                style={"margin-left": "5rem", "margin-right": "5rem", "margin-top": "8px"},
            )
        )
    return all_rows