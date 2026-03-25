import base64
import os
import uuid
import pandas as pd
from django.shortcuts import render
from .models import HousePrice
from sklearn.linear_model import LinearRegression
from rpy2.robjects import r, pandas2ri, numpy2ri, default_converter
from rpy2.robjects.conversion import localconverter
from rpy2.robjects.packages import importr

# Rのパス
os.environ['R_HOME'] = r'C:\Program Files\R\R-4.5.3'
os.environ['PATH'] += r';C:\Program Files\R\R-4.5.3\bin\x64'

def house_list(request):
    # データ取得
    houses = HousePrice.objects.all()

    # 検索条件受け取り
    max_rent = request.GET.get('max_rent')
    max_age = request.GET.get('max_age')

    # フィルタリング処理
    if max_rent:
        houses = houses.filter(rent__lte=max_rent)

    if max_age:
        houses = houses.filter(age__lte=max_age)

    # Pandasデータフレームへ変換
    df = pd.DataFrame(list(houses.values()))
    
    # おすすめ物件推薦
    top_bargains = []

    # 初期値（ifが通らなかった場合の対策）
    reliability_msg = "データが不足しています"
    is_significant = False
    plot_data = ""

    # 0件対策と割安物件計算
    if not df.empty and len(df) > 5:
        X = df[['age', 'distance', 'layout']]
        y = df['rent']

        model = LinearRegression()
        model.fit(X, y)

        df['predicted_rent'] = model.predict(X)

        df['bargain_score'] = df['predicted_rent'] - df['rent']

        top_bargains = df.sort_values(by='bargain_score', ascending=False).head(5).to_dict('records')

        try:
            with localconverter(default_converter + pandas2ri.converter + numpy2ri.converter):
                # PythonのdfをRのr_dfに
                stats = importr('stats')
                r.assign("r_df", df)

                # 重回帰分析
                r_model = r('stats::lm(rent ~ age + distance + layout, data=r_df)')

                # レポート取得
                r_summary = r.summary(r_model)

                # 特定の変数のP値を取り出す
                age_p_value = r('summary(stats::lm(rent ~ age + distance + layout, data=r_df))$coefficients[2, 4]')[0]

                # 判定結果をContextへ
                is_significant = age_p_value < 0.05 # 5%有意
                p_value_rounded = round(float(age_p_value), 4)

                if is_significant:
                    reliability_msg = f"この分析結果は統計的に有意です（p = {p_value_rounded}）"
                else:
                    reliability_msg = f"データ不足のため統計的な有意差は確認できません（p = {p_value_rounded}）"
        
                # 一時保存して表示するためのユニークファイル名
                temp_filename = f"temp_plot_{uuid.uuid4().hex}.png"
                r.assign("temp_filename", temp_filename)

                # ggplot2でグラフを描きファイル保存
                r('''
                library(ggplot2)
                
                # 築年数と家賃の散布図+回帰直線
                p <- ggplot(r_df, aes(x=age, y=rent)) +
                geom_point(alpha=0.5, color="blue") +
                geom_smooth(method="lm", color="red") +
                labs(title="築年数と家賃の関係（AI回帰分析）", x="築年数（年）", y="家賃（万円）") +
                theme_minimal()

                # 画像として保存
                ggsave(temp_filename, plot=p, width=6, height=4, dpi=100)
                ''')

                # 上記をPythonで読み込みBase64に変換
                with open(temp_filename, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                    # HTMLに渡せるよう整理
                    plot_data = f"data:image/png;base64,{encoded_string}"

                # 一時ファイル削除
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
        
        except Exception as e:
            reliability_msg = f"Rの解析中にエラーが発生しました:{e}"

    # データが空の場合スキップ
    if df.empty:
        avg_rent = 0
        corr_rent_age = 0
        ages_list = []
        rents_list = []
    else:
        avg_rent = df['rent'].mean()
        corr_rent_age = df['rent'].corr(df['age'])
        
        avg_rent = round(avg_rent, 1)

        # 相関係数のNan対策
        corr_rent_age = 0 if pd.isna(corr_rent_age) else round(corr_rent_age, 3)

        ages_list = df['age'].tolist()
        rents_list = df['rent'].tolist()

    # テンプレートへ渡すデータの作成
    context = {
        'houses':houses,
        'avg_rent':avg_rent,
        'corr_rent_age':corr_rent_age,
        'ages_list':ages_list,
        'rents_list':rents_list,
        'top_bargains':top_bargains,
        'reliability_msg':reliability_msg,
        'is_significant':is_significant,
        'plot_data':plot_data,
    }

    return render(request, 'real_estate/house_list.html', context)