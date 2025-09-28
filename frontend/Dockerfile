FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Remove proxy configuration for Docker builds
RUN node -e "const pkg = JSON.parse(require('fs').readFileSync('package.json', 'utf8')); delete pkg.proxy; require('fs').writeFileSync('package.json', JSON.stringify(pkg, null, 2));"

EXPOSE 3000

CMD ["npm", "start"]
