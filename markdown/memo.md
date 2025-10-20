**テスト実装の概要（10 行程度）**

1. **インタフェースを定義**  
   ```cpp
   class IScanDriver { virtual void ReqInjectionComplete() = 0;
                       virtual void ReqContrastPhaseSkip(int) = 0; };
   ```

2. **gmock モックを作成**  
   ```cpp
   class MockScanDriver : public IScanDriver {
       MOCK_METHOD(void, ReqInjectionComplete, (), (override));
       MOCK_METHOD(void, ReqContrastPhaseSkip, (int), (override));
   };
   ```

3. **テスト用クラス（ベース）を作る**  
   ```cpp
   class SendSkipCmdTest : public ::testing::TestWithParam<std::tuple<int,int,const char*>> {
       void SetUp() override { mock = std::make_unique<MockScanDriver>();
                               boundary = std::make_unique<TestSendSkipCmd>(mock.get()); }
       std::unique_ptr<MockScanDriver> mock;
       std::unique_ptr<TestSendSkipCmd> boundary;
   };
   ```

4. **10 通りの入力を `::testing::Values(...)` で列挙**  
   ```cpp
   INSTANTIATE_TEST_SUITE_P(AllCases, SendSkipCmdTest, ::testing::Values(
       std::make_tuple(0,3,kPhase_Contrast), std::make_tuple(0,3,kPhase_Saline),
       … , std::make_tuple(1,3,kPhase_Delay)));
   ```

5. **テスト関数で `EXPECT_CALL` を設定**  
   ```cpp
   TEST_P(SendSkipCmdTest, General) {
     auto [completed, cnt, name] = GetParam();
     if (std::string(name)==kPhase_Contrast && completed+1<cnt)
         EXPECT_CALL(*mock, ReqContrastPhaseSkip(completed+2)).Times(1);
     boundary->SendSkipCmdByCurrentContrast(completed, name, cnt);
   }
   ```

6. **gtest の実行**  
   `ctest` でビルド後実行し、10 通りのケースが自動で走査される。  

**ポイント**：  
- `EXPECT_CALL`/`Times(1)` で「スキップが起きる」ケースを検証。  
- 期待しないケースはモックに対して何も宣言しないで関数を呼び出すだけで「呼ばれない」ことをチェック。  
- `INSTANTIATE_TEST_SUITE_P` に10 通りの `tuple` を渡すことで、1 つのテスト関数で全ケースを実行。
