import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.Statement;

public class ConfirmConnect {
    public static void main(String[] args) {
        // プロジェクト直下に sample.db というファイル形式のDBが自動で作られます
        String url = "jdbc:sqlite:sample.db";

        try (Connection conn = DriverManager.getConnection(url);
             Statement stmt = conn.createStatement()) {

            System.out.println("データベース接続成功！トラウマ払拭です！");
            
            // ついでにテーブルも作ってみる
            stmt.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)");
            System.out.println("テーブルの作成もバッチリです！");

        } catch (Exception e) {
            System.out.println("無念のエラー…");
            e.printStackTrace();
        }
    }
}