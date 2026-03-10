import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.Statement;
import java.sql.ResultSet;
import java.util.Random;
import java.util.ArrayList;
import java.util.List;
import com.google.gson.Gson;
import java.io.FileWriter;

public class DataGenerator {

    static class House {
        int id;
        int rent;
        int age;
        int distance;
        int layout;

        // データをセットするための初期化メソッド（コンストラクタ）
        public House(int id, int rent, int age, int distance, int layout) {
            this.id = id;
            this.rent = rent;
            this.age = age;
            this.distance = distance;
            this.layout = layout;
        }
    }

    public static void main(String[] args) {
        // SQLiteのデータベースファイルの場所を指定
        String url = "jdbc:sqlite:real_estate.db";

        // SQL接続
        try (Connection conn = DriverManager.getConnection(url);
             Statement stmt = conn.createStatement()) {

            // 1. テーブル作成
            stmt.execute("DROP TABLE IF EXISTS HousePrice");
            String createTableSQL = "CREATE TABLE HousePrice(id INTEGER,rent INTEGER,age INTEGER,distance INTEGER,layout INTEGER)";
            stmt.execute(createTableSQL);

            // 2. データ挿入
            String insertSQL = "INSERT INTO HousePrice (id, rent, age, distance, layout) VALUES (?, ?, ?, ?, ?)";

            try (PreparedStatement pstmt = conn.prepareStatement(insertSQL)) {
                Random rand = new Random();

                for (int i = 1; i <= 100; i++) {
                    pstmt.setInt(1, i);
                    pstmt.setInt(2, rand.nextInt(11) + 5);
                    pstmt.setInt(3, rand.nextInt(41));
                    pstmt.setInt(4, rand.nextInt(30) + 1);
                    pstmt.setInt(5, rand.nextInt(4) + 1);
                    pstmt.executeUpdate();
                }
            }

            // 3. データ取得とJSON変換
            String selectSQL = "SELECT * FROM HousePrice";

            try (Statement selectStmt = conn.createStatement();
                 ResultSet rs = selectStmt.executeQuery(selectSQL)) {

                // Houseオブジェクトをリストに詰める
                List<House> houseList = new ArrayList<>();

                while (rs.next()) {
                    House house = new House(
                            rs.getInt("id"),
                            rs.getInt("rent"),
                            rs.getInt("age"),
                            rs.getInt("distance"),
                            rs.getInt("layout")
                    );

                    houseList.add(house);
                }

                // JSON変換
                Gson gson = new Gson();
                String jsonOutput = gson.toJson(houseList);

                System.out.println(jsonOutput);

                // JSONファイル出力
                String fileName = "dummy_estate_data.json";

                try (FileWriter wstmt = new FileWriter(fileName)) {
                    wstmt.write(jsonOutput);
                    System.out.println(fileName + " の作成が完了しました。");

                } catch (Exception e) {
                    System.out.println("ファイルの書き込みでエラーが発生しました。");
                    e.printStackTrace();
                }

            }

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}