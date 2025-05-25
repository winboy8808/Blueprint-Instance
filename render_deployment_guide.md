# CRM系统云端部署指南 (Render平台)

## 1. 简介

本指南将引导您如何将我们开发的CRM系统部署到Render云平台。Render是一个易于使用的平台即服务（PaaS），非常适合部署像我们这样的Web应用程序，它会自动处理服务器和数据库的配置。

**部署流程概述：**

1.  注册并登录Render账户。
2.  将CRM系统代码上传到代码托管平台（如GitHub）。
3.  在Render上创建一个新的“Blueprint Instance”，连接您的代码仓库。
4.  Render将根据项目中的 `render.yaml` 文件自动配置Web服务和数据库。
5.  等待部署完成，即可通过Render提供的URL访问您的CRM系统。

**准备工作：**

*   您需要一个代码托管平台的账户（推荐GitHub，免费且与Render集成良好）。
*   您需要一个Render账户（提供免费套餐）。
*   附件中已为您准备好适配Render部署的CRM系统代码包 `crm_system_cloud_package.zip`。

## 2. 准备代码仓库 (GitHub)

1.  **创建GitHub账户**：如果您还没有GitHub账户，请访问 [https://github.com/](https://github.com/) 注册一个。
2.  **创建新仓库**：登录GitHub后，点击右上角的“+”号，选择“New repository”。
    *   给仓库起一个名字，例如 `my-crm-system`。
    *   可以选择“Public”（公开）或“Private”（私有）。Render支持两种类型，私有仓库更安全。
    *   **不要**勾选“Add a README file”、“Add .gitignore”或“Choose a license”，因为我们将上传完整的项目文件。
    *   点击“Create repository”。
3.  **上传代码**：
    *   解压收到的 `crm_system_cloud_package.zip` 文件到本地文件夹。
    *   进入您刚刚创建的GitHub仓库页面，根据页面上的“push an existing repository from the command line”指引，使用Git命令行工具将本地文件夹中的所有文件（包括 `.gitattributes`, `.gitignore`, `app.py`, `Procfile`, `render.yaml`, `requirements.txt`, `run.sh`, `static/`, `templates/`, `database/`, `translations.py`, `user_manual.md` 等）上传到您的GitHub仓库。
    *   如果您不熟悉Git命令行，也可以直接在GitHub仓库页面点击“Add file” -> “Upload files”，然后将解压后的所有文件和文件夹拖拽上传。

## 3. 在Render上部署

1.  **注册Render账户**：访问 [https://render.com/](https://render.com/) 并注册一个账户（可以使用GitHub账户直接登录，方便后续操作）。
2.  **创建Blueprint Instance**：
    *   登录Render后，进入Dashboard（仪表盘）。
    *   点击“New +”按钮，选择“Blueprint”。
    *   连接您的GitHub账户（如果尚未连接）。
    *   从列表中选择您刚刚创建并上传了代码的GitHub仓库（例如 `my-crm-system`）。
    *   点击“Connect”。
3.  **配置服务**：
    *   Render会自动检测到项目根目录下的 `render.yaml` 文件。
    *   它会根据 `render.yaml` 的内容显示将要创建的服务：一个名为 `crm-system` 的Web Service和一个名为 `crm-database` 的PostgreSQL数据库。
    *   **确认服务名称和计划**：默认会使用 `render.yaml` 中定义的名称和免费计划（Free tier）。免费计划有一定限制（如资源、休眠策略），如果您的业务量较大，可以考虑升级到付费计划。
    *   **无需额外配置**：`render.yaml` 已经定义了构建命令 (`pip install -r requirements.txt && flask db upgrade`) 和启动命令 (`gunicorn app:app`)，以及环境变量（包括自动生成的 `SECRET_KEY` 和从数据库服务获取的 `DATABASE_URL`）。
4.  **开始部署**：
    *   确认无误后，点击页面底部的“Create Blueprint Instance”或类似按钮。
    *   Render会开始拉取代码、安装依赖、构建应用、创建数据库并启动服务。
    *   您可以在Render的事件日志中看到详细的部署过程。

## 4. 访问系统

1.  **等待部署完成**：部署过程可能需要几分钟时间。当Web服务的状态显示为“Live”或“Deployed”时，表示部署成功。
2.  **获取访问URL**：在Render的Web服务详情页面，会提供一个 `.onrender.com` 结尾的公开访问URL。例如 `https://crm-system-xxxx.onrender.com`。
3.  **访问系统**：将此URL复制到浏览器地址栏并访问，即可看到CRM系统的登录页面。
4.  **首次登录**：
    *   默认管理员用户名：`admin`
    *   默认管理员密码：`admin123`
    *   请务必在首次登录后修改密码。

## 5. 后续维护与更新

*   **自动部署**：默认情况下，Render会监控您连接的GitHub仓库。每当您向主分支（通常是 `main` 或 `master`）推送新的代码更改时，Render会自动触发重新部署。
*   **数据库备份**：Render的付费数据库计划通常提供自动备份功能。免费计划可能需要手动备份或有一定限制，请查阅Render文档了解详情。
*   **查看日志**：您可以在Render的服务页面查看应用程序的实时日志，方便排查问题。
*   **扩展与升级**：如果系统访问量增加，您可以在Render上轻松升级Web服务和数据库的计划以获得更多资源。

## 6. 注意事项

*   **免费计划限制**：Render的免费Web服务在闲置一段时间后可能会休眠，再次访问时需要几秒钟唤醒。免费数据库也有存储空间等限制。
*   **环境变量**：`render.yaml` 中配置了必要的环境变量。`SECRET_KEY` 由Render自动生成，`DATABASE_URL` 从关联的数据库服务自动注入，无需手动设置。
*   **数据库迁移**：`render.yaml` 中的 `buildCommand` 包含了 `flask db upgrade`，确保每次部署时都会自动应用数据库结构变更。

祝您部署顺利！如果在部署过程中遇到任何Render平台相关的问题，建议查阅Render官方文档或寻求其社区支持。
