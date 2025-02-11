# Usar la imagen base de Nginx
FROM nginx:latest

# Copiar el contenido de la página web al directorio raíz de Nginx
COPY ./html /usr/share/nginx/html

# Exponer el puerto 80 para acceso HTTP
EXPOSE 80

# Cambiar la configuración de Nginx para usar el puerto 8016
RUN sed -i 's/listen       80;/listen       8016;/g' /etc/nginx/conf.d/default.conf
