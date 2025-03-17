#!/usr/bin/bash

# MUST BE DONE IN THIS ORDER 
# SET REQUESTS BEFORE LIMITS

# set request for testing scaling
kubectl set resources deployment adservice --requests=cpu=10m,memory=150Mi
kubectl set resources deployment cartservice --requests=cpu=10m,memory=100Mi
kubectl set resources deployment checkoutservice --requests=cpu=10m,memory=100Mi
kubectl set resources deployment currencyservice --requests=cpu=10m,memory=100Mi
kubectl set resources deployment emailservice --requests=cpu=10m,memory=100Mi
kubectl set resources deployment frontend --requests=cpu=10m,memory=100Mi
kubectl set resources deployment paymentservice --requests=cpu=10m,memory=100Mi
kubectl set resources deployment productcatalogservice --requests=cpu=10m,memory=100Mi
kubectl set resources deployment recommendationservice --requests=cpu=10m,memory=100Mi
kubectl set resources deployment redis-cart --requests=cpu=10m,memory=100Mi
kubectl set resources deployment shippingservice --requests=cpu=10m,memory=100Mi


# set large limit because of horizontal scaling
# based on: 200 clients, 45 rps
kubectl set resources deployment adservice --limits=cpu=100m,memory=250Mi
kubectl set resources deployment cartservice --limits=cpu=100m,memory=150Mi
kubectl set resources deployment checkoutservice --limits=cpu=100m,memory=150Mi
kubectl set resources deployment currencyservice --limits=cpu=100m,memory=150Mi
kubectl set resources deployment emailservice --limits=cpu=100m,memory=150Mi
kubectl set resources deployment frontend --limits=cpu=100m,memory=150Mi
kubectl set resources deployment paymentservice --limits=cpu=100m,memory=150Mi
kubectl set resources deployment productcatalogservice --limits=cpu=100m,memory=150Mi
kubectl set resources deployment recommendationservice --limits=cpu=100m,memory=150Mi
kubectl set resources deployment redis-cart --limits=cpu=100m,memory=150Mi
kubectl set resources deployment shippingservice --limits=cpu=100m,memory=150Mi

