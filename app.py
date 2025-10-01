# uvicorn Chat:app --reload
# http://127.0.0.1:8000

from datetime import datetime
from reactpy import component, html, hooks
from reactpy.backend.fastapi import configure, Options
from fastapi import FastAPI

CSS = """
*{box-sizing:border-box}
html,body,#root{height:100%}
body{
    margin:0;
    font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,Cantarell,Helvetica,Arial;
    background:#212121;           
    color:#eaeaea;
}
.page{
    height:100vh;
    display:flex;
    align-items:center;
    justify-content:center;
    padding:24px; 
    overflow:hidden;                 
}
.card{
    width:100%;
    max-width:700px;
    height: min(800px, calc(100vh - 48px));              
    display:flex;
    flex-direction:column;
    border:1px solid #2b2b2b;
    border-radius:16px;
    background:#242424;          
    overflow:hidden;
    box-shadow:0 8px 24px rgba(0,0,0,.35);
}
/* Header */
.header{
    height:56px;
    display:flex;
    align-items:center;
    gap:12px;
    padding:0 16px;
    background:#242424;
    border-bottom:1px solid #2b2b2b;
}
.header .avatar{width:36px;height:36px;border-radius:50%;background:#2f2f2f}
.header .title{display:flex;flex-direction:column}
.header .name{font-weight:600;font-size:16px}
.header .status{font-size:12px;opacity:.7}
/* Área conversación */
.chat {
    flex:1;
    display:flex;
    flex-direction:column;
    overflow:hidden;
    min-height: 0; 
}
.scroll {
    flex: 1;
    overflow-y: auto;   
    padding: 18px 20px;
    min-height: 0;
    overscroll-behavior:contain;
}

.scroll::-webkit-scrollbar {
    width: 6px; /* delgado */
}

.scroll::-webkit-scrollbar-track {
    background: transparent;  /* sin fondo blanco */
}

.scroll::-webkit-scrollbar-thumb {
    background-color: #303030; /* mismo color que las burbujas */
    border-radius: 8px;
}

.scroll::-webkit-scrollbar-thumb:hover {
    background-color: #3a3a3a; /* un poco más claro al pasar el mouse */
}

/* Firefox */
.scroll {
    scrollbar-width: thin;                 
    scrollbar-color: #303030 transparent;  
}


/* Mensajes */
.row{display:flex;width:100%}
.row.left{justify-content:flex-start}
.row.right{justify-content:flex-end}
.msg{
    max-width:min(78%,720px);
    margin:8px 0;
    padding:10px 12px;
    border-radius:14px;
    line-height:1.4;
    font-size:15px;
    word-wrap:break-word;
    white-space:pre-wrap;
    position:relative;
    background:#303030;           
    border:1px solid #3a3a3a;
    color:#eee;
}
.msg.sent:after{
    content:"";
    position:absolute;top:0;right:-10px;
    border-width:0 0 10px 10px;border-style:solid;
    border-color:transparent transparent transparent #303030;
}
.msg.received:after{
    content:"";
    position:absolute;top:0;left:-10px;
    border-width:0 10px 10px 0;border-style:solid;
    border-color:transparent #303030 transparent transparent;
}
.meta{display:inline-flex;gap:8px;align-items:center;font-size:11px;opacity:.7;margin-top:4px}
/* Composer */
.composer{
    display:grid;
    grid-template-columns:1fr auto;
    gap:10px;
    padding:12px;
    border-top:1px solid #2b2b2b;
    background:#242424;
}
.input{
    border:1px solid #3a3a3a;
    background:#303030;           /* Input solicitado */
    color:#eaeaea;
    border-radius:12px;
    padding:12px 14px;
    font-size:15px;
    outline:none;
}
.input::placeholder{color:#b9b9b9}
.button{
    border:1px solid #ffffff;     /* Botón blanco */
    background:#ffffff;           /* Botón blanco */
    color:#111111;
    border-radius:12px;
    padding:12px 16px;
    font-weight:700;
    cursor:pointer;
}
.button:disabled{opacity:.6;cursor:not-allowed}
@media(max-width:768px){.msg{max-width:88%}}
"""

def ts_now() -> str:
    return datetime.now().strftime("%I:%M %p").lstrip("0")

@component
def ChatApp():
    messages, set_messages = hooks.use_state([
        {"id": 1, "sender": "other", "text": "Lorem Ipsum", "ts": ts_now()},
        {"id": 2, "sender": "me",    "text": "Prueba 2", "ts": ts_now()},
        {"id": 3, "sender": "me",    "text": "Prueba", "ts": ts_now()},
        {"id": 4, "sender": "me",    "text": "Prueba4", "ts": ts_now()},
    ])
    text, set_text = hooks.use_state("")

    def send():
        t = text.strip()
        if not t:
            return
        def _append(prev):
            new = {
                "id": (prev[-1]["id"] + 1) if prev else 1,
                "sender": "me",
                "text": t,
                "ts": ts_now(),
            }
            return prev + [new]
        set_messages(_append)
        set_text("")


    def on_key_down(e):
        # Ignora eventos de composición (IME) que no deben enviar
        if e.get("isComposing"):
            return

        k = (e.get("key") or e.get("code") or "").lower()
        kc = e.get("keyCode") or e.get("which")

        is_enter = (
            k in ("enter", "numpadenter") or
            kc == 13
        )
        no_shift = not (e.get("shiftKey") or False)

        if is_enter and no_shift:
            # ReactPy: prevenir default con acceso tipo dict si existe
            try:
                e["preventDefault"]()
            except Exception:
                pass
            send()


    def bubble(m):
        side = "right" if m["sender"] == "me" else "left"
        klass = "msg sent" if m["sender"] == "me" else "msg received"
        return html.div({"class_name": f"row {side}"},
            html.div({"class_name": klass},
                html.div(m["text"]),
                html.div({"class_name": "meta"}, [html.span(m["ts"])])
            )
        )

    return html.div({"class_name": "page"},
        html.div({"class_name": "card"},
            html.div({"class_name": "header"},
                html.div({"class_name": "avatar"}),
                html.div({"class_name": "title"},
                    html.span({"class_name": "name"}, "Chat"),
                    html.span({"class_name": "status"}, "Funcionando"),
                ),
            ),
            html.div({"class_name": "chat"},
                html.div({"class_name": "scroll"},
                    [bubble(m) for m in messages],
                    html.div({"id": "end"}),
                    html.script("""
                        var end = document.getElementById('end');
                        if (end && end.scrollIntoView) end.scrollIntoView({behavior: 'instant', block: 'end'});
                    """)
                ),
                html.div({"class_name": "composer"},
                    html.input({
                        "class_name": "input",
                        "type": "text",
                        "placeholder": "Escribe un mensaje…",
                        "value": text,
                        "on_change": lambda e: set_text(e["target"]["value"]),
                        "on_key_down": on_key_down,
                        "autocomplete": "off",
                    }),
                    html.button({
                        "class_name": "button",
                        "type": "button",       
                        "on_click": lambda e: send(),  
                    }, "Enviar"),
                )
            )
        )
    )

app = FastAPI()
configure(
    app,
    ChatApp,
    options=Options(
        head=html.head(
            html.meta({"charset": "utf-8"}),
            html.meta({"name": "viewport", "content": "width=device-width, initial-scale=1"}),
            html.style(CSS),
        )
    ),
)
