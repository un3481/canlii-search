# canlii-search
Docker container that performs a search in canlii.org

## run
```
sudo docker build . -t un3481/canlii-search:v1
sudo docker run -p 8080:80 --env-file .env un3481/canlii-search:v1
```