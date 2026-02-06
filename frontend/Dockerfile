FROM node:22 AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build --configuration=production

FROM nginx:alpine
# On utilise /*/ pour dire "le premier dossier qu'on trouve dans dist"
COPY --from=build /app/dist/*/browser /usr/share/nginx/html
EXPOSE 80