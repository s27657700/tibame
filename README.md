tibame專案  AI carcar
功能:
1.拍照識車
2.價格預測
3.車款推薦
4.附近車廠
5.即時熱搜榜

負責項目:價格預測、即時熱搜榜

價格預測實作過程:
首先從網路上爬取所需的車款價格資訊，將文字訊息存入MongoDB，各網站的資料爬取完後將MongoDB中的資料取出進行彙整、清洗、抽取特徵及建模，將最後的資料進行one-hot encoding並在MySQL中建立相關的one-hot特徵表，以供後續使用價格預測功能時可以從這些表格選取資料進行預測，將模型及一些對使用者輸入特徵的處理寫成function崁在line bot。

價格預測難題及解決方法:
建模後把資料帶入測試時，發現將顏色、車型及年分固定只改變里程數的情況下，預測出來的價格並不會隨著里程數改變而有波動，甚至輸入較低的里程數有時候還會出現較高的價格。首先嘗試改變模型參數及套用其他迴歸模型，雖然R2 score有可能略有上升，但是里程數的問題依然存在。再來試著對資料做處理，試過只取里程數萬以上的數字去建模，試過對里程數分等級，效果都不盡理想，最後把里程數分完等級之後再做倒數，此時的價格才正確的依循里程數的上升而下降，或是里程數下降而價格上升，沿著分級並倒數的方向去測試分級的單位，最後以一萬做為分級單位。舉例說明資料改變的前後，例如原始里程數為25000，以一萬為單位分完級後該欄的資料為3，再將3作倒數，最後資料變成0.3333

即時熱搜榜實作過程::
在使用者使用價格預測功能的時候，將輸入的資料傳送到kafka，寫一隻程式將kafka內的資料下載並儲存到MySQL，再由另一隻程式將這些使用者輸入的車款做次數排序後定期的將排行榜傳到redis中。

即時熱搜榜難題及解決方法:
下載kafka中資料的consumer常常因session.timeout時間到而掛掉，常常需要人員去手動重新開啟。將consumer包裝成Docker Image並設定container自動重啟。
