import pandas as pd
from django.shortcuts import render
from .models import HousePrice
from sklearn.linear_model import LinearRegression

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

    # 0件対策と割安物件計算
    if not df.empty and len(df) > 1:
        X = df[['age', 'distance', 'layout']]
        y = df['rent']

        model = LinearRegression()
        model.fit(X, y)

        df['predicted_rent'] = model.predict(X)

        df['bargain_score'] = df['predicted_rent'] - df['rent']

        top_bargains = df.sort_values(by='bargain_score', ascending=False).head(5).to_dict('records')

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
    }

    return render(request, 'real_estate/house_list.html', context)