# Code Deploy Handson

## 参考サイト

-  [CodeDeployを使ってアプリケーションをEC2インスタンスへデプロイする #AWS - Qiita](https://qiita.com/kooohei/items/5c28aa56f961ac300e2c)

## 手順

### Code Deploy Agent を SSM でインストールする

```
aws ssm send-command \
    --document-name "AWS-ConfigureAWSPackage" \
    --instance-ids "i-092b82ea8abe72be8" \
    --parameters '{"action":["Install"],"installationType":["Uninstall and reinstall"],"name":["AWSCodeDeployAgent"]}'
```