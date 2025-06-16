from plotter import generate_ARR_plot, generate_pie, generate_plot, generate_heatmap, generate_hexbin
from flask import Flask, render_template, request
import sqlite3
import pandas as pd


app = Flask(__name__)

def get_game_list():
    conn = sqlite3.connect("database/Personal.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT game FROM records")
    games = [row[0] for row in cursor.fetchall()]
    conn.close()
    return games

@app.route("/", methods=["GET", "POST"])
def index():
  conn = sqlite3.connect("database/Personal.db")
  selected_game = request.form.get("game")
  games = get_game_list()

  query1 = "SELECT game, rank_weight FROM records WHERE game != 'Rumble Racing' GROUP BY game"
  query2 = "SELECT platform, game, achievement_num, COUNT(*) as count FROM achievements WHERE 1=1"
  query3 = "SELECT game, category, COUNT(DISTINCT(category)) AS count FROM records WHERE 1=1"
  query4 = "SELECT date, COUNT(date) as date_count FROM records WHERE date != 'N/A'"
  query5 = "SELECT game, category, AVG(position) AS position FROM records WHERE category == '3lap' OR category == 'flap' GROUP BY game, category"
  query6 = "SELECT track, rank_weight FROM records WHERE game != 'Rumble Racing' AND rank_weight != 'N/A'" 

  params = []

  if selected_game:
      query2 += " AND game = ?"
      query3 += " AND game = ?"
      query4 += " AND game = ?"
      query6 += " AND game = ?"
      params.append(selected_game)
      query2 += " GROUP BY game"
      query3 += " GROUP BY category"
      query4 += " GROUP BY date"
      df2 = pd.read_sql_query(query2, conn, params=params)
      df3 = pd.read_sql_query(query3, conn, params=params)
      plot_data2 = generate_pie(df2["game"], df2["achievement_num"], "Achievement Number For Game")
      plot_data3 = generate_pie(df3["category"], df3["count"], "Categories Ran For Selected Game")
  else:
    query2 += " GROUP BY platform"
    query3 += " GROUP BY game"
    query4 += " GROUP BY date"
    df2 = pd.read_sql_query(query2, conn)
    df3 = pd.read_sql_query(query3, conn)
    plot_data2 = generate_pie(df2["platform"], df2["count"])
    plot_data3 = generate_pie(df3["game"], df3["count"], "Categories Ran")

  df1 = pd.read_sql_query(query1, conn)
  df4 = pd.read_sql_query(query4, conn, params=params)
  df5 = pd.read_sql_query(query5, conn)
  df6 = pd.read_sql_query(query6, conn, params=params)
  conn.close()

  plot_data1 = generate_ARR_plot(df1)
  plot_data4 = generate_plot(df4)
  plot_data5 = generate_heatmap(df5)
  plot_data6 = generate_hexbin(df6)

  return render_template(
  "index.html",
  plot_data1=plot_data1,
  plot_data2=plot_data2,
  plot_data3=plot_data3,
  plot_data4=plot_data4,
  plot_data5=plot_data5,
  plot_data6=plot_data6,
  games=games,
  selected_game=selected_game
)

if __name__ == "__main__":
  app.run(debug=True)
