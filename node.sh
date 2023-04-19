#!/bin/sh
cd /root/NFTMarketplace-Frontend/src && npx hardhat node && npx hardhat compile
cd /root/NFTMarketplace-Frontend/src && npx hardhat node && npx hardhat compile
cd /root/NFTMarketplace-Frontend/ && npx hardhat run --network localhost scripts/deploy.ts