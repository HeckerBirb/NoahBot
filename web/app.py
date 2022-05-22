from flask import Flask, request, jsonify
import mariadb

app = Flask(__name__)

COLUMNS = [
    "discord_id",
    "name",
    "rank",
    "hof_pos",
    "vip_level",
    "machine_creator",
    "challenge_creator",
    "banned",
]

"""
CREATE TABLE users (
    discord_id INT NOT NULL,
    time TIMESTAMP NOT NULL DEFAULT current_timestamp(),
    name VARCHAR(255),
    hof_pos INT,
    vip_level INT,
    machine_creator BOOL,
    challenge_creator BOOL,
    banned BOOL,
    rank VARCHAR(32)
);
"""


@app.route("/queue", methods=["GET", "POST"])
def queue():
    conn = mariadb.connect(
        user="root", password="password", host="db", database="noahbot"
    )
    cur = conn.cursor()
    if request.method == "GET":
        stmt = f"DELETE FROM users ORDER BY time ASC RETURNING {','.join(COLUMNS)}"
        cur.execute(stmt)
        results = [
            {
                "discord_id": discord_id,
                "name": name,
                "rank": rank,
                "hof_pos": hof_pos,
                "vip_level": vip_level,
                "machine_creator": machine_creator,
                "challenge_creator": challenge_creator,
                "banned": banned,
            }
            for (
                discord_id,
                name,
                rank,
                hof_pos,
                vip_level,
                machine_creator,
                challenge_creator,
                banned,
            ) in cur.fetchall()
        ]
        conn.commit()
        return jsonify(results)
    elif request.method == "POST":
        stmt = f"INSERT INTO users ({','.join(COLUMNS)}) VALUES ({','.join('?' for _ in range(len(COLUMNS)))})"
        values = tuple([request.json.get(x) for x in COLUMNS])
        cur.execute(stmt, values)
        conn.commit()
        return jsonify({"result": "ok"})


app.run(host="0.0.0.0", port=5000)
