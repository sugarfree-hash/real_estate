import pandas as pd
from django.shortcuts import render
from .models import HousePrice

def house_list(request):
    # データ取得
    houses = HousePrice.objects.all()

    # Pandasデータフレームへ変換
    df = pd.DataFrame(list(houses.values()))

    # 平均値・相関係数
    avg_rent = df['rent'].mean()
    corr_rent_age = df['rent'].corr(df['age'])

    avg_rent = round(avg_rent, 1)
    corr_rent_age = round(corr_rent_age, 3)

    # テンプレートへ渡すデータの作成
    context = {
        'houses':houses,
        'avg_rent':avg_rent,
        'corr_rent_age':corr_rent_age,
    }

    return render(request, 'real_estate/house_list.html', context)