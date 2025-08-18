# Frontend Dockerfile for Vite dev server
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --no-audit --no-fund
COPY . .
EXPOSE 5174
ENV HOST=0.0.0.0
CMD ["npm", "run", "dev", "--", "--host", "--port", "5174"] 