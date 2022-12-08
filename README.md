# MineSweeper
### 使用python2.7, MongoDB及Redis

### 有三種版本
1. LocalGame  
本機玩，可以多人一起玩，不過只能同一台玩

2. ClientServer  
可以多人連線一起玩，有增加User機制及token機制，User是存在Server下的Players資料夾，每個人都是一筆檔案

3. ClientServerWithDb  
將玩家資料寫入DB，使用Redis控管token，如果Token過期(預設10分鐘沒有動作時會過期)，需要重開才能登入。每個動作都會寫進db，也會存動作完的結果


