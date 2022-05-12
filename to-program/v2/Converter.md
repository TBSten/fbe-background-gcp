
# Converterリファクタリングについて

# 新構成

## コンストラクタ(fbe :FBEFormat)

各プロパティをfbeをもとに初期化

## `convert(fbe)`

プログラムに変換する

## ユーティリティ

### `get_item(itemId ItemId)`

アイテムを取得する。存在しない場合はエラー。

### `get_sym(itemId :ItemId)`

Symを取得する

### `get_flow(itemId :ItemId)`

Flowを取得する

### `variable(name :str, formula :Formula)`

変数に代入する。宣言していない場合は宣言も行う

### `indent :int`

現在のインデント数

### `indent_str :str`

インデント文字、通常"  "

### `indent_up()`

インデントを１つあげる

### `indent_down()`

インデントを１つ下げる

### `line(data :str)`

行出力キューに追加

### `flush()`

行出力キューの値を取得しクリアする

## オーバーライドメソッド

### 基本系

#### `define_variable(name :str, formula :Formula)`

変数を宣言する

#### `assign_variable(name :str, formula :Formula)`

変数に値を代入する

#### `comment(msg :str)`

1行コメント

### item系

#### `terminal_start_sym(sym :Sym, text:str)`

|引数|オプション名|
|---|---|
|text|テキスト|

#### `terminal_end_sym(sym :Sym, hasReturnValue :bool, returnValue :Formula )`

|引数|オプション名|
|---|---|
|hasReturnValue|戻り値を返す|
|returnValue|戻り値|

#### `calc_sym(sym :Sym, formula :Formula, variable :str)`

|引数|オプション名|
|---|---|
|formula|式|
|variable|代入先変数|

#### `output_sym(sym :Sym, target :Formula)`

|引数|オプション名|
|---|---|
|target|表示対象|

#### `input_sym(sym :Sym, variable :str, is_number :bool)`

|引数|オプション名|
|---|---|
|variable|入力先変数|
|is_number|数字で入力|

#### `while_sym(sym :Sym, childId :ItemId, condition :Formula, timing :str)`

|引数|オプション名|
|---|---|
|condition|ループ条件|
|timing|判定タイミング|

#### `for_sym(sym :Sym, childId :ItemId, variable :str, first :Formula, condition :Formula, increment :Formula)`

|引数|オプション名|
|---|---|
|variable|ループ変数|
|first|初期値|
|condition|条件|
|increment|増分|

#### `if_sym(sym :Sym, yesFlowId :ItemId,noFlowId :ItemId,condition :Formula)`

|引数|オプション名|
|---|---|
|condition|条件|

#### `switch_sym(sym :Sym,childIds :ItemId[], condition :Formula)`

|引数|オプション名|
|---|---|
|condition|条件|

#### `prepare_sym(sym :Sym, target :str, target_type :str, first :Formula, count :int[], simple_disp :bool)`

|引数|オプション名|
|---|---|
|target|準備対象|
|target_type|種類|
|first|初期値|
|count|要素数|
|simple_disp|簡易表示|

#### `process_sym(sym :Sym, process_name :str)`

|引数|オプション名|
|---|---|
|process_name|処理名|

#### `flow(sym :Sym,childId :ItemId, tag :str)`

|引数|オプション名|
|---|---|
|tag|タグ|

# その他ユーティリティ

## `noExistsItemError(itemId :ItemId)`

get_item()などでアイテムが存在しなかった場合に出力
