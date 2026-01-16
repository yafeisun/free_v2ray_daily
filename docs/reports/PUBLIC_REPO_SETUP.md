# 公开库配置指南

本文档说明如何配置双仓库架构，将节点自动发布到公开库。

## 架构说明

- **私有库 (v2raynode)**: 存放代码和运行环境
- **公开库 (v2ray-nodes)**: 只存放生成的节点信息

## 配置步骤

### 1. 创建公开库

1. 访问 https://github.com/new
2. 仓库名称填写：`v2ray-nodes`
3. 设置为 **Public**（公开）
4. 不要初始化 README、.gitignore 或 license
5. 点击 **Create repository**

### 2. 生成GitHub Personal Access Token

1. 访问 https://github.com/settings/tokens
2. 点击 **Generate new token** → **Generate new token (classic)**
3. 设置token名称：`v2ray-nodes-publish`
4. 选择权限（Scopes）：
   - ✅ `repo` (完整仓库访问权限)
   - ✅ `workflow` (工作流权限)
5. 点击 **Generate token**
6. **重要**：复制生成的token（只显示一次）

### 3. 配置GitHub Secrets

在私有库（v2raynode）中配置Secrets：

1. 访问私有库的Settings页面
2. 左侧菜单选择 **Secrets and variables** → **Actions**
3. 点击 **New repository secret**
4. 添加以下Secret：

   | Name | Value | 说明 |
   |------|-------|------|
   | `PUBLISH_TOKEN` | 刚才生成的token | 用于推送节点到公开库 |
   | `GIT_EMAIL` | your-email@example.com | Git提交邮箱（可选） |
   | `GIT_NAME` | Your Name | Git提交用户名（可选） |

5. 点击 **Add secret** 保存

### 4. 测试工作流

1. 将 `.github/workflows/publish_nodes.yml` 提交到私有库
2. 推送到GitHub
3. 访问私有库的 **Actions** 标签页
4. 选择 **Publish Nodes to Public Repo** 工作流
5. 点击 **Run workflow** 手动触发
6. 查看运行日志，确认节点已成功推送到公开库

### 5. 验证公开库

1. 访问公开库：`https://github.com/你的用户名/v2ray-nodes`
2. 检查是否包含以下文件：
   - `README.md`
   - `nodelist.txt`
   - `nodetotal.txt`
   - `webpage.txt`
   - `subscription.txt`
3. 验证节点内容是否正确

## 工作流说明

### 自动运行

- **触发时间**: 每日北京时间早上8点（UTC 0点）
- **执行流程**:
  1. 从私有库检出代码
  2. 安装Python依赖
  3. 运行节点收集器
  4. 从公开库检出代码
  5. 复制节点文件到公开库
  6. 提交并推送到公开库

### 手动触发

1. 访问私有库的 **Actions** 标签页
2. 选择 **Publish Nodes to Public Repo** 工作流
3. 点击 **Run workflow**
4. 选择分支（通常是main）
5. 点击 **Run workflow** 开始运行

## 常见问题

### Q: 推送失败，提示权限不足？

A: 检查以下几点：
1. PUBLISH_TOKEN是否正确配置
2. Token是否有`repo`和`workflow`权限
3. 公开库是否已创建

### Q: 公开库没有更新？

A: 检查以下几点：
1. 查看Actions运行日志
2. 确认节点文件是否生成
3. 检查是否有git冲突

### Q: 如何修改公开库名称？

A: 如果需要使用其他名称，修改 `.github/workflows/publish_nodes.yml` 中的仓库名称：
```yaml
repository: ${{ github.repository_owner }}/你的仓库名
```

### Q: 如何只推送特定文件？

A: 修改 `.github/workflows/publish_nodes.yml` 中的Copy步骤，只复制需要的文件。

## 安全建议

1. **Token安全**:
   - 不要将token提交到代码库
   - 定期更换token
   - 设置token过期时间（建议90天）

2. **权限最小化**:
   - 只授予必要的权限
   - 不要使用管理员token

3. **监控**:
   - 定期检查Actions运行日志
   - 监控公开库的访问情况

## 维护建议

1. **定期更新**:
   - 每月检查一次工作流运行状态
   - 更新依赖包版本

2. **备份**:
   - 定期备份节点文件
   - 保留最近7天的节点数据

3. **文档更新**:
   - 更新README.md中的使用说明
   - 记录重要的配置变更

## 联系支持

如有问题，请：
1. 查看Actions运行日志
2. 检查GitHub Secrets配置
3. 参考本文档的常见问题部分