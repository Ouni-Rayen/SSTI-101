from flask import Flask, request, render_template_string
import os

app = Flask(__name__)

# Create the flag at startup (Render filesystem is ephemeral)
FLAG_PATH = "/tmp/securinets_flag"
FLAG_CONTENT = "Securinets{SSTI_1s_n0t_just_ab0ut_RCE_y0u_n33d_t0_l00k_cl0s3r}"

if not os.path.exists(FLAG_PATH):
    try:
        with open(FLAG_PATH, "w") as f:
            f.write(FLAG_CONTENT)
    except Exception:
        # Fallback if /tmp is restricted for some reason
        FLAG_PATH = os.path.join(os.getcwd(), "securinets_flag")
        with open(FLAG_PATH, "w") as f:
            f.write(FLAG_CONTENT)

# The vulnerable template (only the name is injected raw)
TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="logo.jpg" type="image/jpeg">
    <title>Personal Card Generator</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background-color: #0B1426;
            color: #F0F4F8;
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background-color: #111C2E;
            border: 1px solid #2D3748;
            border-radius: 12px;
            padding: 40px;
            width: 100%;
            max-width: 520px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.45);
        }
        h1 {
            text-align: center;
            margin-bottom: 8px;
            font-weight: 600;
            letter-spacing: 0.5px;
            font-size: 1.6rem;
        }
        .subtitle {
            text-align: center;
            color: #A0AEC0;
            margin-bottom: 32px;
            font-size: 0.95rem;
        }
        label {
            display: block;
            margin-bottom: 6px;
            color: #A0AEC0;
            font-size: 0.9rem;
        }
        input, textarea {
            width: 100%;
            padding: 12px 14px;
            margin-bottom: 18px;
            background: #0B1426;
            border: 1px solid #2D3748;
            border-radius: 6px;
            color: #F0F4F8;
            font-size: 1rem;
            transition: border-color 0.2s;
        }
        input:focus, textarea:focus {
            outline: none;
            border-color: #A0AEC0;
        }
        button {
            width: 100%;
            padding: 14px;
            background: #F0F4F8;
            color: #0B1426;
            border: none;
            border-radius: 6px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            margin-top: 6px;
        }
        button:hover {
            background: #A0AEC0;
            transform: translateY(-1px);
        }
        .card {
            margin-top: 35px;
            padding: 25px;
            background: #0B1426;
            border: 1px solid #2D3748;
            border-radius: 8px;
        }
        .card h2 {
            margin-bottom: 14px;
            font-size: 1.35rem;
            color: #F0F4F8;
        }
        .card p {
            color: #A0AEC0;
            line-height: 1.55;
            margin-bottom: 8px;
        }
        .card strong {
            color: #CBD5E0;
        }
        .hint {
            margin-top: 25px;
            text-align: center;
            font-size: 0.8rem;
            color: #718096;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to SecuriNets ISI</h1>
        <p class="subtitle">Create your custom profile card</p>

        <form method="POST">
            <label>Name </label>
            <input type="text" name="name" placeholder="Your name" required value="{{ name or '' }}">

            <label>Display Name</label>
            <input type="text" name="display_name" placeholder="How others see you" value="{{ display_name or '' }}">

            <label>Bio</label>
            <textarea name="bio" rows="3" placeholder="A short bio...">{{ bio or '' }}</textarea>

            <label>Favourite Quote</label>
            <input type="text" name="quote" placeholder="Your favourite quote" value="{{ quote or '' }}">

            <button type="submit">Generate Card</button>
        </form>

        {% if name is defined and name %}
        <div class="card">
            <h2>Hello {{ name }}!</h2>
            <p><strong>Display Name:</strong> {{ display_name | e }}</p>
            <p><strong>Bio:</strong> {{ bio | e }}</p>
            <p><strong>Quote:</strong> {{ quote | e }}</p>
        </div>
        {% endif %}

        <p class="hint">SecuriNets ISI freindly CTF</p>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name", "")
        display_name = request.form.get("display_name", "")
        bio = request.form.get("bio", "")
        quote = request.form.get("quote", "")

        # Only the 'name' field is passed unescaped → SSTI
        return render_template_string(
            TEMPLATE,
            name=name,
            display_name=display_name,
            bio=bio,
            quote=quote
        )

    return render_template_string(TEMPLATE)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
