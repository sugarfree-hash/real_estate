library(DBI)
library(RSQLite)
library(dplyr)

# 1. データベースに接続
con <- dbConnect(RSQLite::SQLite(), "real_estate.db")

# 2. テーブルの一覧確認
dbListTables(con)

# 3. データをRの表形式へ
my_data <- dbReadTable(con, "houseprice")

# 4. 接続終了
dbDisconnect(con)

# 5. 重回帰分析
model <- lm(rent ~ age + distance + layout, data = my_data)

# 6. 中身の確認
head(my_data)
summary(my_data)
summary(model) # 解析結果の表示