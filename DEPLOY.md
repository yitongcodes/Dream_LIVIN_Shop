# Dream LIVIN Shop 部署指南

## 部署到 ai-builders.space

### 方法 1: 使用 Docker 部署（推荐）

1. **构建 Docker 镜像**
   ```bash
   docker build -t dream-livin-shop .
   ```

2. **运行容器**
   ```bash
   docker run -d \
     -p 8000:8000 \
     -e AI_BUILDER_TOKEN=your_token_here \
     -e PORT=8000 \
     -e MAX_IMAGE_COUNT=1000 \
     --name dream-livin-shop \
     dream-livin-shop
   ```

### 方法 2: 使用 AI Builder Space 平台部署

如果 ai-builders.space 提供部署服务，请按照以下步骤：

1. **准备环境变量**
   - `AI_BUILDER_TOKEN`: 您的 AI Builder Space API token
   - `PORT`: 应用端口（通常由平台自动设置）
   - `MAX_IMAGE_COUNT`: 最大图片数量（默认 1000）

2. **连接 GitHub 仓库**
   - 在 ai-builders.space 平台连接您的 GitHub 仓库
   - 设置自动部署（当 push 到 main 分支时）

3. **配置域名**
   - 设置子域名：`dream-livin-shop.ai-builders.space`
   - 配置 SSL/HTTPS（通常平台自动处理）

### 方法 3: 使用 MCP 部署工具

如果您有 MCP 部署工具可用，请使用相应的 API 进行部署。

## 验证部署

部署完成后，访问：
- 前端：`https://dream-livin-shop.ai-builders.space/`
- API 文档：`https://dream-livin-shop.ai-builders.space/docs`
- OpenAPI：`https://dream-livin-shop.ai-builders.space/openapi.json`

## 环境变量配置

确保在生产环境中设置以下环境变量：

```env
AI_BUILDER_TOKEN=your_actual_token
PORT=8000
MAX_IMAGE_COUNT=1000
```

## 注意事项

- ✅ `.env` 文件已添加到 `.gitignore`，不会被提交
- ✅ Dockerfile 已配置多阶段构建
- ✅ 前端已构建并包含在 Docker 镜像中
- ✅ 端口配置支持环境变量 `PORT`
