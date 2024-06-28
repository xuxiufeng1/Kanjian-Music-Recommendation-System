# 音乐推荐系统部署指南

本指南介绍了如何部署本音乐推荐系统，包括以下组件：

*   **机器学习训练**: 使用 Vertex AI Workbench Notebooks 训练推荐模型。
*   **模型存储**: 将训练好的模型存储在 Google Cloud Storage (GCS) 中。
*   **推荐服务**: 使用 Cloud Function 部署一个 API 端点，提供推荐服务。 

## 组件部署指南

### 1. 机器学习模型训练 (Vertex AI Workbench Notebooks)

*   **文件**: `music-recommendation-system-using-spotify-dataset-3bfa2b5e-a0fe-418c-864e-4552f13051f1.ipynb`
*   **部署步骤**:
    1.  在 Google Cloud Console 中打开 [Vertex AI Workbench](https://console.cloud.google.com/vertex-ai/workbench)。
    2.  创建一个新的 Notebook 实例，并选择合适的机器配置。
    3.  将 `music-recommendation-system-using-spotify-dataset-3bfa2b5e-a0fe-418c-864e-4552f13051f1.ipynb` 文件的内容复制到 Notebook 中。
    4.  运行 Notebook 中的代码，进行模型训练。训练完成后，模型会被保存到 GCS。

### 2. 模型存储 (Google Cloud Storage)

*   **文件**: `model.joblib`
*   **部署步骤**:
    1.  模型训练完成后，会自动将 `model.joblib` 文件保存到指定的 GCS 路径。

### 3. 音乐推荐服务 (Cloud Function)

*   **文件**: `main.py`, `requirements.txt`
*   **部署步骤**:
    1.  在 Google Cloud Console 中打开 [Cloud Functions](https://console.cloud.google.com/functions)。
    2.  创建一个新的 Cloud Function，选择 Python 作为运行时环境。
    3.  将 `main.py` 文件的内容复制到 Cloud Function 的代码编辑器中。
    4.  将 `requirements.txt` 文件的内容复制到 Cloud Function 的 "需求" 设置中，以安装必要的依赖项。
    5.  部署 Cloud Function。部署完成后，你将获得一个 API 端点，可以用来调用推荐服务。

## 访问推荐服务

部署完成后，你可以使用以下方式访问推荐服务：

*   **发送 HTTP 请求到 Cloud Function 端点**: 使用工具（例如 `curl` 或 Postman）发送 HTTP 请求到 Cloud Function 的触发器 URL，请求体中包含歌曲列表。
*   **集成到你的应用程序中**: 在你的应用程序代码中调用 Cloud Function 端点，并将推荐结果集成到你的应用中。 

## 注意事项

*   确保你的 Vertex AI Workbench Notebook 实例和 Cloud Function 具有访问 GCS 存储桶的权限。
*   在 `main.py` 文件中，你需要根据实际情况修改项目 ID、存储桶名称和其他配置参数。
