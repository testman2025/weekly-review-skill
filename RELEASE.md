# 发布指南

## 1. 推送到 GitHub（门槛最低）

当前环境未配置 GitHub CLI / Token，因此已在本地完成 `git init` 和初始 commit。接下来需要手动创建远程仓库并推送。

### 步骤 A：在 GitHub 网页创建空仓库

1. 访问 https://github.com/new
2. 仓库名填 `weekly-review-skill`
3. **不要**勾选 "Initialize this repository with a README"、.gitignore 或 license（本地已有）
4. 创建后复制仓库 HTTPS 或 SSH 地址

### 步骤 B：本地推送

```bash
cd D:\test\workbuddy\weekly-review-skill
git remote add origin https://github.com/EDY/weekly-review-skill.git
# 或 SSH：git remote add origin git@github.com:EDY/weekly-review-skill.git
git branch -M main
git push -u origin main
```

推送后即完成 GitHub 开源发布。若仓库名为其他名称，请替换 URL。

## 2. 发布到 SkillHub / WorkBuddy 技能市场

WorkBuddy 生态支持通过 SkillHub 共享 skill。常见路径：

### 2.1 通过 SkillHub 官网（图形化，门槛低）

1. 登录 https://skillhub.cn（需与 WorkBuddy 同一账号）
2. 进入「发布技能」页面
3. 填写：
   - 技能名称：`weekly-review-skill`
   - 描述：基于 workbuddy.db 的周度复盘分析 skill，固化复盘底座，不固化每周成品
   - 分类：`productivity` / `效率工具`
   - 标签：`workbuddy`, `weekly-review`, `mcp`, `复盘`
4. 上传入口文件 `skills/workbuddy/SKILL.md`
5. 提交审核，等待 1-7 个工作日

### 2.2 通过 CNB (cnb.cool) Git 仓库发布

SkillHub/cnb.cool 支持从 Git 仓库直接安装 skill：

```bash
# 用户安装方式（发布后在 README 中提供）
npx skills add https://cnb.cool/EDY/weekly-review-skill.git --agent codebuddy -y --copy
```

发布步骤：

1. 注册/登录 https://cnb.cool
2. 创建仓库 `EDY/weekly-review-skill`
3. 添加远程并推送：
   ```bash
   git remote add cnb https://cnb.cool/EDY/weekly-review-skill.git
   git push cnb main
   ```
4. 在 SkillHub 后台关联该仓库并提交审核

## 3. 作为 MCP server 发布

由于本仓库同时提供 MCP server，也可被 Claude Desktop、Cline、Cursor 等支持 MCP 的客户端使用：

```json
{
  "mcpServers": {
    "weekly-review": {
      "command": "weekly-review-mcp"
    }
  }
}
```

可提交到 [MCP Community Servers](https://github.com/modelcontextprotocol/servers) 等 MCP 生态列表（需按各平台规范提 PR）。

## 4. 版本管理

建议每次改进后打 tag：

```bash
git tag v0.1.0
git push origin v0.1.0
```

WorkBuddy / SkillHub 通常按 tag 拉取稳定版本。

## 5. 当前状态

- [x] 本地代码完成
- [x] CLI 测试通过
- [x] MCP server 测试通过
- [x] 本地 git 仓库初始化并提交
- [x] GitHub 远程仓库创建与 push → https://github.com/testman2025/weekly-review-skill （公开仓库，已开源发布）
- [ ] SkillHub / WorkBuddy 市场提交（需登录 skillhub.cn 网页，OAuth 审核，步骤见第 2 节）
- [ ] cnb.cool 发布（需 CNB_TOKEN，当前环境无凭据，步骤见第 2.2 节）

> GitHub 已是门槛最低的开源平台，仓库已公开可克隆、可 `npx skills add` 安装、可作为 MCP server 接入任意兼容客户端。
