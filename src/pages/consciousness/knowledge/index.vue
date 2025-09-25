<template>
  <view class="knowledge-base">
    <view class="module-header">
      <text class="title">知识库</text>
      <view class="knowledge-stats">
        <view class="stat-item">
          <text class="stat-value">{{ totalDocuments }}</text>
          <text class="stat-label">文档总数</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ totalNotes }}</text>
          <text class="stat-label">笔记数量</text>
        </view>
      </view>
    </view>

    <view class="knowledge-container">
      <!-- 导航标签 -->
      <view class="nav-tabs">
        <button
          class="tab-btn"
          :class="{ active: currentTab === 'library' }"
          @click="currentTab = 'library'"
        >
          书库
        </button>
        <button
          class="tab-btn"
          :class="{ active: currentTab === 'notes' }"
          @click="currentTab = 'notes'"
        >
          笔记
        </button>
        <button
          class="tab-btn"
          :class="{ active: currentTab === 'brain' }"
          @click="currentTab = 'brain'"
        >
          云脑
        </button>
      </view>

      <!-- 书库看板 -->
      <view v-if="currentTab === 'library'" class="library-section">
        <view class="section-header">
          <text class="section-title">我的书库</text>
        </view>

        <!-- 文档列表 -->
        <view class="documents-grid">
          <view
            v-for="(doc, index) in documents"
            :key="index"
            class="document-card"
            :class="{ 'has-dropdown': showDocOptionsModal && optionsDoc && optionsDoc.id === doc.id }"
          >
            <view class="card-main">
              <view class="doc-icon">
                <text class="file-icon">{{ getFileIcon(doc.type) }}</text>
              </view>
              <view class="doc-info">
                <text class="doc-name">{{ doc.name }}</text>
                <text class="doc-meta">{{ formatFileSize(doc.size) }} · {{ doc.uploadTime }}</text>
              </view>
              <view class="doc-actions">
                <button
                  class="action-btn"
                  @click="previewDocument(doc)"
                >
                  预览
                </button>
                <button
                  class="action-btn"
                  @click="showDocOptions(doc)"
                >
                  更多
                </button>
              </view>
            </view>
            <!-- 展开的操作按钮：在卡片下方横向排列 -->
            <view
              v-if="showDocOptionsModal && optionsDoc && optionsDoc.id === doc.id"
              class="doc-actions-expanded"
            >
              <view class="action-btn" @click="downloadDocument(doc)">下载文档</view>
              <view class="action-btn" @click="showDocumentDetail(doc)">查看详情</view>
              <view class="action-btn danger" @click="openDeleteModal(doc)">删除文档</view>
            </view>

          </view>
        </view>


        <!-- 悬浮按钮 -->
        <view class="float-btn" @click="showUploadModal">
          <text class="btn-text">上传文档</text>
        </view>

        <!-- 上传文档弹窗 -->
        <view v-if="showUpload" class="upload-modal">
          <view class="modal-content">
            <view class="modal-header">
              <text class="modal-title">上传文档</text>
              <button class="close-btn" @click="closeUploadModal">×</button>
            </view>
            <view class="upload-area">
              <view
                class="drop-zone"
                @click="triggerFileInput"
                @touchstart="handleTouchStart"
                @touchend="handleTouchEnd"
              >
                <text class="drop-icon">📄</text>
                <text class="drop-text">点击选择文件</text>
                <text class="drop-hint">支持 PDF、TXT、Word 文档</text>
              </view>
            </view>
            <view class="upload-list" v-if="selectedFiles.length > 0">
              <view
                v-for="(file, index) in selectedFiles"
                :key="index"
                class="upload-item"
              >
                <text class="file-name">{{ file.name }}</text>
                <text class="file-size">{{ formatFileSize(file.size) }}</text>
                <button
                  class="remove-btn"
                  @click="removeFile(index)"
                >
                  移除
                </button>
              </view>
            </view>
            <view class="modal-footer">
              <button
                class="cancel-btn"
                @click="closeUploadModal"
              >
                取消
              </button>
              <button
                class="confirm-btn"
                @click="uploadFiles"
                :disabled="selectedFiles.length === 0"
              >
                上传
              </button>
            </view>
          </view>
        </view>
        <!-- 文档详情暗色弹窗（与上传弹窗风格统一） -->
        <view v-if="showDetailModal" class="upload-modal">
          <view class="modal-content">
            <view class="modal-header">
              <text class="modal-title">文档详情</text>
              <button class="close-btn" @click="closeDetailModal">×</button>
            </view>
            <view class="modal-body">

              <view class="detail-item">
                <text class="detail-label">文件名：</text>
                <text class="detail-value">{{ selectedDoc ? selectedDoc.name : '未知' }}</text>
              </view>
              <view class="detail-item">
                <text class="detail-label">大小：</text>
                <text class="detail-value">{{ selectedDoc ? formatFileSize(selectedDoc.size || 0) : formatFileSize(0) }}</text>
              </view>
              <view class="detail-item">
                <text class="detail-label">类型：</text>
                <text class="detail-value">{{ selectedDoc ? selectedDoc.type : '未知' }}</text>
              </view>
              <view class="detail-item">
                <text class="detail-label">上传时间：</text>
                <text class="detail-value">{{ selectedDoc ? selectedDoc.uploadTime : '未知' }}</text>
              </view>
            </view>
            <view class="modal-footer">
              <button class="confirm-btn" @click="closeDetailModal">确定</button>
            </view>
          </view>
        </view>
        <!--

        -->
        <view v-if="showDeleteModal" class="upload-modal">
          <view class="modal-content">
            <view class="modal-header">
              <text class="modal-title">确认删除</text>
              <button class="close-btn" @click="closeDeleteModal">×</button>
            </view>
            <view class="modal-body">
              <text>确定要删除文档“{{ selectedDoc ? selectedDoc.name : '' }}”吗？此操作不可恢复。</text>
            </view>
            <view class="modal-footer">
              <button class="cancel-btn" @click="closeDeleteModal">取消</button>
              <button class="confirm-btn danger-btn" @click="confirmDelete">删除</button>
            </view>
          </view>
        </view>


      </view>

      <!-- 笔记模块 -->
      <view v-if="currentTab === 'notes'" class="notes-section">
        <view class="section-header">
          <text class="section-title">我的笔记</text>
          <view class="folder-select">


            <select v-model="currentFolder" class="folder-select-input">
              <option value="">根目录</option>
              <option v-for="folder in folders" :key="folder.id" :value="folder.id">
                {{ folder.name }}
              </option>
            </select>
            <button class="new-folder-btn" @click="showNewFolderModal">
              <text class="plus-icon">+</text>
              新建文件夹
            </button>
          </view>
        </view>

        <!-- 笔记列表 -->
        <view class="notes-grid">
          <view
            v-for="(note, index) in filteredNotes"
            :key="index"
            class="note-card"
            @click="openNote(note)"
          >
            <view class="note-header">
              <text class="note-title">{{ note.title }}</text>
              <text class="note-time">{{ note.updateTime }}</text>
            </view>
            <text class="note-preview">{{ note.preview }}</text>
          </view>
        </view>

        <!-- 笔记编辑器 -->
        <view v-if="showEditor" class="note-editor">
          <view class="editor-header">
            <input
              type="text"
              v-model="currentNote.title"
              class="title-input"
              placeholder="笔记标题"
            >
            <view class="editor-actions">
              <button
                class="action-btn save"
                @click="saveNote"
              >
                保存
              </button>
              <button
                class="action-btn close"
                @click="closeEditor"
              >
                关闭
              </button>
            </view>
          </view>
          <textarea
            v-model="currentNote.content"
            class="editor-content"
            placeholder="开始编写你的笔记..."
          ></textarea>
          <view class="editor-footer">
            <text class="folder-info">
              保存至：{{ currentNote.folderId ? ((folders.find(f => f.id === currentNote.folderId) || {}).name || '根目录') : '根目录' }}
            </text>
          </view>
        </view>

        <!-- 悬浮按钮 -->
        <view class="float-btn" @click="createNewNote">
          <text class="btn-text">新建笔记</text>
        </view>

        <!-- 新建文件夹弹窗 -->
        <view v-if="showFolderModal" class="folder-modal">
          <view class="modal-content">
            <view class="modal-header">
              <text class="modal-title">新建文件夹</text>
              <button class="close-btn" @click="closeFolderModal">×</button>
            </view>
            <view class="modal-body">
              <input
                type="text"
                v-model="newFolderName"
                class="folder-name-input"
                placeholder="输入文件夹名称"
              >
            </view>
            <view class="modal-footer">
              <button
                class="cancel-btn"
                @click="closeFolderModal"
              >
                取消
              </button>
              <button
                class="confirm-btn"
                @click="createFolder"
                :disabled="!newFolderName"
              >
                创建
              </button>
            </view>
          </view>
        </view>
      </view>

      <!-- 第二大脑模块 -->
      <view v-if="currentTab === 'brain'" class="brain-section">


        <!-- 知识图谱 -->
        <view class="knowledge-graph">
          <view class="graph-header">
            <text class="graph-title">知识图谱</text>
            <view class="graph-actions">
              <button
                class="action-btn"
                :class="{ active: graphView === 'network' }"
                @click="graphView = 'network'"
              >
                网络
              </button>
              <button
                class="action-btn"
                :class="{ active: graphView === 'tree' }"
                @click="graphView = 'tree'"
              >
                树形
              </button>
            </view>
          </view>

          <view class="graph-container">
            <!-- 网络视图 -->
            <view v-if="graphView === 'network'" class="network-view">
              <view
                v-for="(node, index) in knowledgeNodes"
                :key="index"
                class="node"
                :style="{
                  left: node.x + '%',
                  top: node.y + '%'
                }"
              >
                <view class="node-content">
                  <text class="node-title">{{ node.title }}</text>
                  <text class="node-type">{{ node.type }}</text>
                </view>
                <view class="node-connections">
                  <view
                    v-for="(connection, cIndex) in node.connections"
                    :key="cIndex"
                    class="connection"
                  ></view>
                </view>
              </view>
            </view>

            <!-- 树形视图 -->
            <view v-else class="tree-view">
              <view class="tree-node root">
                <text class="node-title">我的知识体系</text>
                <view class="tree-branches">
                  <view
                    v-for="(branch, index) in knowledgeBranches"
                    :key="index"
                    class="tree-branch"
                  >
                    <view class="branch-node">
                      <text class="node-title">{{ branch.title }}</text>
                      <view class="sub-branches">
                        <view
                          v-for="(sub, sIndex) in branch.subs"
                          :key="sIndex"
                          class="sub-branch"
                        >
                          <text class="node-title">{{ sub.title }}</text>
                        </view>
                      </view>
                    </view>
                  </view>
                </view>
              </view>
            </view>
          </view>
        </view>


      </view>


    </view>
  </view>
</template>

<script>
import { documentsAPI, notesAPI } from '@/utils/api.js'
import authManager from '@/utils/auth.js'
import { getFileIcon, formatFileSize } from '@/utils/fileUtils'

export default {
  name: 'KnowledgeBase',

  data() {
    return {
      currentTab: 'library',
      loading: false,
      totalDocuments: 0,
      totalNotes: 8,
      showUpload: false,
      showEditor: false,
      showFolderModal: false,
      showPreview: false,
      showDocOptionsModal: false,
      // 用于弹窗展示的选中文档
      selectedDoc: null,
      // 用于“更多”下拉菜单定位的选中文档
      optionsDoc: null,

      selectedFiles: [],
      showDetailModal: false,
      showDeleteModal: false,


      currentFolder: '',
      newFolderName: '',
      currentNote: {
        id: '',
        title: '',
        content: '',
        folderId: ''
      },
      folders: [
        { id: '1', name: '工作笔记' },
        { id: '2', name: '学习笔记' },
        { id: '3', name: '项目记录' }
      ],
      documents: [],
      notes: [],
      editorTools: [
        { icon: 'B', action: 'bold' },
        { icon: 'I', action: 'italic' },
        { icon: 'U', action: 'underline' },
        { icon: '📝', action: 'list' },
        { icon: '🔗', action: 'link' }
      ],
      previewDoc: null,
      touchStartTime: 0,

      graphView: 'network',

      knowledgeNodes: [],
      knowledgeBranches: []
    }
  },
  computed: {
    filteredNotes() {
      if (!this.currentFolder) {
        // 根目录：显示没有文件夹ID或文件夹ID为空的笔记
        return this.notes.filter(note => !note.folderId || note.folderId === '' || note.folderId === null)
      }
      // 特定文件夹：显示该文件夹的笔记
      return this.notes.filter(note => note.folderId === this.currentFolder)
    }
  },
  async mounted() {
    // 检查登录状态
    if (!authManager.isLoggedIn()) {
      authManager.requireLogin()
      return
    }

    await this.loadKnowledgeData()
  },
  methods: {
    // 导入的工具函数
    getFileIcon,
    formatFileSize,
    // 加载知识库数据
    async loadKnowledgeData() {
      this.loading = true
      try {
        const documents = await documentsAPI.getDocuments()

        // 格式化文档数据，确保字段一致性
        this.documents = documents.map(doc => {
          const filename = doc.filename || ''
          const parts = filename.toLowerCase().split('.')
          const extFromName = parts.length > 1 ? parts.pop() : ''
          const extFromMime = (doc.file_type || '').toLowerCase().split('/').pop()
          const type = extFromName || extFromMime || ''
          return {
            id: doc.id,
            name: doc.filename,
            type,
            file_type: doc.file_type, // 兼容性字段
            size: doc.file_size,
            uploadTime: doc.uploaded_at ? doc.uploaded_at.split('T')[0] : '',
            url: doc.file_path,
            status: doc.status
          }
        })


        this.totalDocuments = documents.length

        // 加载笔记数据
        await this.loadNotesData()
      } catch (error) {
        this.handleError(error, '加载数据失败', '加载知识库数据失败:')
      } finally {
        this.loading = false
      }
    },

    // 通知父组件刷新统计数据
    notifyParentRefresh() {
      // 通过事件总线或者直接调用父组件方法
      uni.$emit('refreshDashboardStats')
    },

    // 加载笔记数据
    async loadNotesData() {
      try {
        // 加载所有笔记列表（不按文件夹过滤，前端进行过滤）
        const notes = await notesAPI.getAllNotes()
        // 确保前端字段名一致性：将后端的folder_id转换为folderId
        this.notes = notes.map(note => ({
          ...note,
          folderId: note.folder_id
        }))
        this.totalNotes = notes.length

        // 加载文件夹列表
        const folders = await notesAPI.getFolders()
        this.folders = folders

      } catch (error) {
        console.error('加载笔记数据失败:', error)
        // 如果API调用失败，保持原有的模拟数据
        this.totalNotes = 0
        this.notes = []
        this.folders = [
          { id: '1', name: '工作笔记' },
          { id: '2', name: '学习笔记' },
          { id: '3', name: '项目记录' }
        ]
      }
    },

    // 使用uni-app的文件上传方法
    async uploadFileWithUni(file) {
      const userId = authManager.getCurrentUserId()
      if (!userId) {
        throw new Error('用户未登录')
      }

      return new Promise((resolve, reject) => {
        uni.uploadFile({
          url: `http://localhost:8000/api/user/documents/upload?user_id=${encodeURIComponent(userId)}`,
          filePath: file.path,
          name: 'file',
          header: {
            'Authorization': authManager.getToken() ? `Bearer ${authManager.getToken()}` : ''
          },
          success: (uploadRes) => {
            try {
              const response = JSON.parse(uploadRes.data)
              if (response.code === 200) {
                resolve(response.data)
              } else {
                reject(new Error(response.message || '文档上传失败'))
              }
            } catch (error) {
              reject(new Error('解析响应数据失败'))
            }
          },
          fail: () => {
            reject(new Error('网络请求失败'))
          }
        })
      })
    },

    // 通用模态框控制方法
    openModal(type) {
      switch (type) {
        case 'upload':
          this.showUpload = true
          break
        case 'detail':
          this.showDetailModal = true
          break
        case 'delete':
          this.showDeleteModal = true
          break
        case 'folder':
          this.showFolderModal = true
          break
      }
    },

    // 通用文档选择方法（深拷贝并关闭选项）
    selectDocumentForModal(doc, modalType) {
      this.selectedDoc = JSON.parse(JSON.stringify(doc))
      this.openModal(modalType)
      this.closeDocOptions()
    },

    // 通用错误处理方法
    handleError(error, message, logPrefix = '') {
      console.error(logPrefix, error)
      uni.showToast({
        title: message,
        icon: 'error'
      })
    },
    closeModal(type) {
      switch (type) {
        case 'upload':
          this.showUpload = false
          this.selectedFiles = []
          break
        case 'detail':
          this.showDetailModal = false
          break
        case 'delete':
          this.showDeleteModal = false
          break
        case 'folder':
          this.showFolderModal = false
          this.newFolderName = ''
          break
      }
    },

    // 保持原有方法名以兼容现有模板
    showUploadModal() {
      this.openModal('upload')
    },
    closeUploadModal() {
      this.closeModal('upload')
    },
    triggerFileInput() {
      uni.chooseFile({
        count: 10,
        type: 'all',
        extension: ['.pdf', '.txt', '.doc', '.docx'],
        success: (res) => {
          const files = res.tempFiles.map(file => ({
            name: file.name,
            size: file.size,
            path: file.path
          }))
          this.selectedFiles = [...this.selectedFiles, ...files]
        }
      })
    },

    async uploadFiles() {
      if (this.selectedFiles.length === 0) {
        uni.showToast({
          title: '请选择要上传的文件',
          icon: 'none'
        })
        return
      }

      // 显示上传进度
      uni.showLoading({
        title: '上传中...'
      })

      try {
        let uploadedCount = 0
        const uploadPromises = this.selectedFiles.map(async (file) => {
          try {
            let result

            // 检查是否在uni-app环境中
            if (typeof uni !== 'undefined' && uni.uploadFile) {
              // 使用uni-app的上传方法
              result = await this.uploadFileWithUni(file)
            } else {
              // 使用标准的fetch上传
              result = await documentsAPI.uploadDocument(file)
            }

            // 将后端返回的文档数据添加到列表
            const doc = {
              id: result.document.id,
              name: result.document.filename,
              type: result.document.file_type,
              file_type: result.document.file_type, // 兼容性字段
              size: result.document.file_size,
              uploadTime: result.document.uploaded_at.split('T')[0],
              url: result.document.file_path,
              status: result.document.status
            }

            this.documents.unshift(doc)
            this.totalDocuments++
            uploadedCount++

            return doc
          } catch (error) {
            console.error('文件上传失败:', error)
            uni.showToast({
              title: `${file.name} 上传失败`,
              icon: 'error'
            })
            throw error
          }
        })

        // 等待所有文件上传完成
        await Promise.all(uploadPromises)

        uni.hideLoading()
        uni.showToast({
          title: '上传成功',
          icon: 'success'
        })
        this.closeUploadModal()

        // 重新加载文档列表以确保数据同步
        await this.loadKnowledgeData()

        // 通知父组件更新统计数据
        this.notifyParentRefresh()

      } catch (error) {
        uni.hideLoading()
        console.error('上传过程中出现错误:', error)
      }
    },
    getFileType(filename) {
      const ext = filename.split('.').pop().toLowerCase()
      if (ext === 'pdf') return 'pdf'
      if (ext === 'txt') return 'txt'
      if (['doc', 'docx'].includes(ext)) return 'doc'
      return 'unknown'
    },
    async previewDocument(doc) {
      try {
        // 获取文档预览URL
        const previewUrl = documentsAPI.getDocumentPreviewUrl(doc.id)

        // #ifdef H5
        // 在H5环境中，直接在新窗口中打开预览
        // 后端已经设置了正确的Content-Disposition: inline头，浏览器会直接显示而不是下载
        window.open(previewUrl, '_blank')
        // #endif

        // #ifndef H5
        // 在uni-app环境中，根据文件类型选择预览方式
        if (doc.type === 'pdf' || doc.file_type === 'pdf' ||
            doc.type === '.pdf' || doc.file_type === '.pdf' ||
            doc.type === 'txt' || doc.file_type === 'txt' ||
            doc.type === '.txt' || doc.file_type === '.txt' ||
            doc.type === 'md' || doc.file_type === 'md' ||
            doc.type === '.md' || doc.file_type === '.md') {
          // 可预览的文件类型，使用系统浏览器打开
          // #ifdef APP-PLUS
          plus.runtime.openURL(previewUrl)
          // #endif
          // #ifdef MP
          // 小程序环境暂不支持预览，提示用户下载
          uni.showToast({
            title: '请下载后查看',
            icon: 'none'
          })
          // #endif
        } else {
          // 其他文件类型（如Word文档），下载后用系统应用打开
          const downloadUrl = documentsAPI.getDocumentDownloadUrl(doc.id)
          uni.downloadFile({
            url: downloadUrl,
            success: (res) => {
              if (res.statusCode === 200) {
                uni.openDocument({
                  filePath: res.tempFilePath,
                  fileType: doc.type || doc.file_type,
                  success: () => {
                    // 文档打开成功
                  },
                  fail: (err) => {
                    console.error('打开文档失败', err)
                    uni.showToast({
                      title: '预览失败，请尝试下载查看',
                      icon: 'none'
                    })
                  }
                })
              }
            },
            fail: (err) => {
              console.error('下载文件失败', err)
              this.handleError(err, '预览失败', '下载文件失败:')
            }
          })
        }
        // #endif
      } catch (error) {
        this.handleError(error, '预览失败', '预览文档失败:')
      }
    },
    closePreview() {
      // 移除预览相关的状态
      this.showPreview = false
      this.previewDoc = null
    },
    showDocOptions(doc) {
      // 计算“更多”按钮相对于视口的位置，使弹窗显示在其正下方


      // 切换当前弹窗
      if (this.showDocOptionsModal && this.optionsDoc && this.optionsDoc.id === doc.id) {
        this.showDocOptionsModal = false
        this.optionsDoc = null
      } else {
        this.optionsDoc = doc
        this.showDocOptionsModal = true
      }
    },

    closeDocOptions() {
      this.showDocOptionsModal = false
      this.optionsDoc = null
    },



    // 下载文档
    downloadDocument(doc) {
      try {
        const downloadUrl = documentsAPI.getDocumentDownloadUrl(doc.id)

        // #ifdef H5
        // 在H5环境中直接下载
        const link = document.createElement('a')
        link.href = downloadUrl
        link.download = doc.name
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        // #endif

        // #ifndef H5
        // 在uni-app中使用下载API
        uni.downloadFile({
          url: downloadUrl,
          success: (res) => {
            if (res.statusCode === 200) {
              uni.showToast({
                title: '下载成功',
                icon: 'success'
              })
            }
          },
          fail: (err) => {
            console.error('下载失败:', err)
            uni.showToast({
              title: '下载失败',
              icon: 'error'
            })
          }
        })
        // #endif

        this.closeDocOptions()
      } catch (error) {
        this.handleError(error, '下载失败', '下载文档失败:')
      }
    },

    // 删除文档（改为自定义暗色确认弹窗）
    deleteDocument(doc) {
      this.openDeleteModal(doc)
    },

    openDeleteModal(doc) {
      this.selectDocumentForModal(doc, 'delete')
    },
    closeDeleteModal() {
      this.closeModal('delete')
    },
    async confirmDelete() {
      if (!this.selectedDoc) return
      try {
        uni.showLoading({ title: '删除中...' })
        const doc = this.selectedDoc
        // 调用删除API
        await documentsAPI.deleteDocument(doc.id)

        // 从列表中移除
        const index = this.documents.findIndex(d => d.id === doc.id)
        if (index > -1) {
          this.documents.splice(index, 1)
          this.totalDocuments--
        }

        this.closeModal('delete')
        uni.hideLoading()
        uni.showToast({ title: '删除成功', icon: 'success' })
        this.notifyParentRefresh()
      } catch (error) {
        uni.hideLoading()
        this.handleError(error, '删除失败', '删除文档失败:')
      }
    },



    // 查看文档详情（使用自定义暗色弹窗，统一风格）
    showDocumentDetail(doc) {
      this.selectDocumentForModal(doc, 'detail')
    },
    closeDetailModal() {
      this.closeModal('detail')
    },

    showNewFolderModal() {
      this.openModal('folder')
    },
    closeFolderModal() {
      this.closeModal('folder')
    },
    async createFolder() {
      if (!this.newFolderName.trim()) {
        uni.showToast({
          title: '请输入文件夹名称',
          icon: 'none'
        })
        return
      }

      try {
        uni.showLoading({
          title: '创建中...'
        })

        const folderData = {
          name: this.newFolderName,
          parent_id: null // 暂时只支持根目录文件夹
        }

        const newFolder = await notesAPI.createFolder(folderData)
        this.folders.push(newFolder)
        this.closeModal('folder')

        uni.showToast({
          title: '文件夹创建成功',
          icon: 'success'
        })
      } catch (error) {
        console.error('创建文件夹失败:', error)
        uni.showToast({
          title: '创建失败',
          icon: 'error'
        })
      } finally {
        uni.hideLoading()
      }
    },
    createNewNote() {
      this.currentNote = {
        id: '',
        title: '',
        content: '',
        folderId: this.currentFolder || null,  // 确保根目录时为null
        tags: []
      }
      this.showEditor = true
    },
    openNote(note) {
      this.currentNote = { ...note }
      this.showEditor = true
    },
    closeEditor() {
      this.showEditor = false
    },
    async saveNote() {
      if (!this.currentNote.title.trim()) {
        uni.showToast({
          title: '请输入笔记标题',
          icon: 'none'
        })
        return
      }

      try {
        uni.showLoading({
          title: '保存中...'
        })

        const noteData = {
          title: this.currentNote.title,
          content: this.currentNote.content,
          folder_id: this.currentNote.folderId || null,
          tags: this.currentNote.tags || []
        }

        let savedNote
        // 如果是新建笔记
        if (!this.currentNote.id) {
          savedNote = await notesAPI.createNote(noteData)
          // 确保前端字段名一致性：将后端的folder_id转换为folderId
          if (savedNote.folder_id !== undefined) {
            savedNote.folderId = savedNote.folder_id
          }
          this.notes.unshift(savedNote)
          this.totalNotes++
          uni.showToast({
            title: '笔记创建成功',
            icon: 'success'
          })
        } else {
          // 更新现有笔记
          savedNote = await notesAPI.updateNote(this.currentNote.id, noteData)
          // 确保前端字段名一致性
          if (savedNote.folder_id !== undefined) {
            savedNote.folderId = savedNote.folder_id
          }
          const index = this.notes.findIndex(note => note.id === this.currentNote.id)
          if (index !== -1) {
            this.notes.splice(index, 1, savedNote)
          }
          uni.showToast({
            title: '笔记更新成功',
            icon: 'success'
          })
        }

        this.closeEditor()
        // 通知父组件刷新统计数据
        this.notifyParentRefresh()

      } catch (error) {
        console.error('保存笔记失败:', error)
        uni.showToast({
          title: '保存失败',
          icon: 'error'
        })
      } finally {
        uni.hideLoading()
      }
    },

    addTag() {
      if (this.newTag && !this.currentNote.tags.includes(this.newTag)) {
        this.currentNote.tags.push(this.newTag)
        this.newTag = ''
      }
    },
    removeTag(index) {
      this.currentNote.tags.splice(index, 1)
    },
    handleTouchStart() {
      this.touchStartTime = Date.now()
    },
    handleTouchEnd() {
      const touchDuration = Date.now() - this.touchStartTime
      if (touchDuration < 200) { // 短按触发文件选择
        this.triggerFileInput()
      }
    },

  }
}
</script>

<style lang="scss">
// 公共模态框样式
.modal-base {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #1f1f1f;
  border-radius: 16px;
  width: 90%;
  padding: 24px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;

  .modal-title {
    font-size: 20px;
    font-weight: 500;
  }

  .close-btn {
    background: none;
    border: none;
    color: rgba(255, 255, 255, 0.6);
    font-size: 24px;
    cursor: pointer;

    &:hover {
      color: #fff;
    }
  }
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;

  .cancel-btn,
  .confirm-btn {
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 14px;
    cursor: pointer;
  }

  .cancel-btn {
    background: transparent;
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: rgba(255, 255, 255, 0.8);

    &:hover {
      background: rgba(255, 255, 255, 0.05);
    }
  }

  .confirm-btn {
    background: #1890ff;
    border: none;
    color: #fff;

    &:hover {
      background: #40a9ff;
    }

    &:disabled {
      background: rgba(24, 144, 255, 0.5);
      cursor: not-allowed;
    }
  }

  .danger-btn {
    background: #ff4d4f !important;
    &:hover {
      background: #ff7875 !important;
    }
  }
}

.knowledge-base {
  height: 100%;

  .module-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;

    .title {
      font-size: 24px;
      font-weight: bold;
    }

    .knowledge-stats {
      display: flex;
      gap: 20px;

      .stat-item {
        text-align: right;

        .stat-value {
          font-size: 24px;
          font-weight: bold;
          color: #1890ff;
          display: block;
        }

        .stat-label {
          font-size: 14px;
          color: rgba(255, 255, 255, 0.6);
        }
      }
    }
  }

  .knowledge-container {
    .nav-tabs {
      display: flex;
      gap: 16px;
      margin-bottom: 24px;

      .tab-btn {
        padding: 8px 24px;
        border-radius: 8px;
        font-size: 16px;
        background: transparent;
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: rgba(255, 255, 255, 0.8);
        cursor: pointer;
        transition: all 0.3s;

        &:hover {
          background: rgba(255, 255, 255, 0.05);
        }

        &.active {
          background: rgba(255, 255, 255, 0.1);
          border-color: rgba(255, 255, 255, 0.3);
          color: #fff;
        }
      }
    }

    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;

      .section-title {
        font-size: 20px;
        font-weight: 500;
      }
    }

    .documents-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 20px;

      .document-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 16px;
        display: flex;
        flex-direction: column;
        position: relative;

        // 主要内容区域（图标、信息、操作按钮）
        .card-main {
          display: flex;
          align-items: center;
          gap: 16px;
        }

        &.has-dropdown {
          z-index: 100;
        }

        .doc-icon {
          .file-icon {
            font-size: 24px;
          }
        }

        .doc-info {
          flex: 1;

          .doc-name {
            font-size: 16px;
            font-weight: 500;
            margin-bottom: 4px;
            display: block;
          }

          .doc-meta {
            font-size: 12px;
            color: rgba(255, 255, 255, 0.4);
          }
        }

        // 通用按钮样式
        .action-btn {
          padding: 6px 12px;
          border-radius: 6px;
          font-size: 14px;
          background: rgba(255, 255, 255, 0.1);
          color: #fff;
          border: none;
          cursor: pointer;

          &:hover {
            background: rgba(255, 255, 255, 0.15);
          }

          &.danger {
            background: rgba(220, 53, 69, 0.1);
            color: #dc3545;

            &:hover {
              background: rgba(220, 53, 69, 0.2);
            }
          }
        }

        .doc-actions {
          display: flex;
          gap: 8px;
          position: relative;
        }

        // 展开的操作按钮样式
        .doc-actions-expanded {
          display: flex;
          gap: 8px;
          margin-top: 12px;
          padding-top: 12px;
          border-top: 1px solid rgba(255, 255, 255, 0.1);

          .action-btn {
            flex: 1;
            text-align: center;
          }
        }
      }
    }

    .upload-modal {
      @extend .modal-base;

      .modal-content {
        @extend .modal-content;
        max-width: 600px;
        .modal-body {
          .detail-item {
            display: flex;
            margin-bottom: 12px;
            .detail-label {
              color: rgba(255, 255, 255, 0.6);
              min-width: 80px;
            }
            .detail-value {
              color: rgba(255, 255, 255, 0.9);
              flex: 1;
            }
          }
        }

        .upload-area {
          .drop-zone {
            border: 2px dashed rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 40px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            user-select: none;

            &:active {
              border-color: #1890ff;
              background: rgba(24, 144, 255, 0.05);
            }

            .drop-icon {
              font-size: 48px;
              margin-bottom: 16px;
              display: block;
            }

            .drop-text {
              font-size: 16px;
              margin-bottom: 8px;
              display: block;
            }

            .drop-hint {
              font-size: 14px;
              color: rgba(255, 255, 255, 0.4);
            }
          }
        }

        .upload-list {
          margin-top: 20px;

          .upload-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            margin-bottom: 8px;

            .file-name {
              flex: 1;
              font-size: 14px;
            }

            .file-size {
              font-size: 12px;
              color: rgba(255, 255, 255, 0.4);
            }

            .remove-btn {
              padding: 4px 8px;
              border-radius: 4px;
              font-size: 12px;
              background: #ff4d4f;
              color: #fff;
              border: none;
              cursor: pointer;

              &:hover {
                background: #ff7875;
              }
            }
          }
        }


      }
    }

    .notes-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 20px;

      .note-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 16px;
        cursor: pointer;
        transition: all 0.3s;

        &:hover {
          background: rgba(255, 255, 255, 0.08);
        }

        .note-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;

          .note-title {
            font-size: 16px;
            font-weight: 500;
          }

          .note-time {
            font-size: 12px;
            color: rgba(255, 255, 255, 0.4);
          }
        }

        .note-preview {
          font-size: 14px;
          color: rgba(255, 255, 255, 0.6);
          margin-bottom: 16px;
          display: -webkit-box;
          -webkit-line-clamp: 3;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
      }
    }

    .note-editor {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: #1f1f1f;
      z-index: 1000;
      display: flex;
      flex-direction: column;

      .editor-header {
        padding: 16px 24px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;

        .title-input {
          background: transparent;
          border: none;
          font-size: 20px;
          font-weight: 500;
          color: #fff;
          width: 60%;

          &:focus {
            outline: none;
          }
        }

        .editor-actions {
          display: flex;
          gap: 12px;

          .action-btn {
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 14px;
            cursor: pointer;

            &.save {
              background: #1890ff;
              color: #fff;
              border: none;

              &:hover {
                background: #40a9ff;
              }
            }

            &.close {
              background: transparent;
              border: 1px solid rgba(255, 255, 255, 0.2);
              color: rgba(255, 255, 255, 0.8);

              &:hover {
                background: rgba(255, 255, 255, 0.05);
              }
            }
          }
        }
      }

      .editor-content {
        flex: 1;
        padding: 24px;
        background: transparent;
        border: none;
        color: #fff;
        font-size: 16px;
        line-height: 1.6;
        resize: none;

        &:focus {
          outline: none;
        }
      }

      .editor-footer {
        padding: 16px 24px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);

        .folder-info {
          font-size: 14px;
          color: rgba(255, 255, 255, 0.6);
        }
      }
    }
  }
}

.float-btn {
  position: fixed;
  right: 24px;
  bottom: 24px;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 16px;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    background: rgba(255, 255, 255, 0.15);
    transform: translateY(-2px);
  }

  .btn-text {
    font-weight: 500;
  }
}

.folder-select {
  display: flex;
  align-items: center;
  gap: 12px;

  .folder-select-input {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 6px;
    padding: 8px 12px;
    color: #fff;
    font-size: 14px;
    min-width: 120px;

    &:focus {
      outline: none;
      border-color: #1890ff;
    }

    // 下拉选项样式
    option {
      background: rgba(0, 0, 0, 0.9);
      color: #fff;
      padding: 8px 12px;
      border: none;

      &:hover {
        background: rgba(255, 255, 255, 0.1);
      }

      &:checked {
        background: rgba(24, 144, 255, 0.2);
      }
    }
  }

  .new-folder-btn {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 14px;
    background: rgba(255, 255, 255, 0.1);
    color: #fff;
    border: none;
    cursor: pointer;

    &:hover {
      background: rgba(255, 255, 255, 0.15);
    }

    .plus-icon {
      font-size: 16px;
    }
  }
}

.folder-modal {
  @extend .modal-base;

  .modal-content {
    @extend .modal-content;
    max-width: 400px;

    .modal-body {
      .folder-name-input {
        width: 100%;
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 6px;
        padding: 12px;
        color: #fff;
        font-size: 16px;

        &:focus {
          outline: none;
          border-color: #1890ff;
        }
      }
    }


  }
}

.brain-section {


  .knowledge-graph {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 24px;

    .graph-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;

      .graph-title {
        font-size: 20px;
        font-weight: 500;
      }

      .graph-actions {
        display: flex;
        gap: 12px;

        .action-btn {
          padding: 8px 16px;
          border-radius: 8px;
          font-size: 14px;
          background: transparent;
          border: 1px solid rgba(255, 255, 255, 0.2);
          color: rgba(255, 255, 255, 0.8);
          cursor: pointer;

          &:hover {
            background: rgba(255, 255, 255, 0.05);
          }

          &.active {
            background: rgba(255, 255, 255, 0.1);
            border-color: rgba(255, 255, 255, 0.3);
            color: #fff;
          }
        }
      }
    }

    .graph-container {
      height: 400px;
      position: relative;

      .network-view {
        height: 100%;

        .node {
          position: absolute;
          transform: translate(-50%, -50%);

          .node-content {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 12px;
            min-width: 120px;
            text-align: center;

            .node-title {
              font-size: 14px;
              font-weight: 500;
              display: block;
              margin-bottom: 4px;
            }

            .node-type {
              font-size: 12px;
              color: rgba(255, 255, 255, 0.4);
            }
          }

          .node-connections {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;

            .connection {
              position: absolute;
              background: rgba(255, 255, 255, 0.1);
              height: 2px;
              transform-origin: left center;
            }
          }
        }
      }

      .tree-view {
        height: 100%;

        .tree-node {
          &.root {
            text-align: center;

            .node-title {
              font-size: 18px;
              font-weight: 500;
              margin-bottom: 24px;
              display: block;
            }
          }

          .tree-branches {
            display: flex;
            justify-content: center;
            gap: 40px;

            .tree-branch {
              .branch-node {
                .node-title {
                  font-size: 16px;
                  font-weight: 500;
                  margin-bottom: 16px;
                  display: block;
                }

                .sub-branches {
                  display: flex;
                  flex-direction: column;
                  gap: 12px;

                  .sub-branch {
                    .node-title {
                      font-size: 14px;
                      color: rgba(255, 255, 255, 0.8);
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }


  // Global floating dropdown overlay
  .doc-options-overlay {
    position: fixed;
    z-index: 2000;

    .dropdown-container {
      background: rgba(255, 255, 255, 0.05) !important;
      border-radius: 12px !important;
      padding: 8px !important;
      width: 300px !important; // 与 document-card 宽度保持一致
      border: 1px solid rgba(255, 255, 255, 0.1) !important;
      backdrop-filter: blur(10px) !important;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4) !important;
      display: flex !important;
      flex-direction: column !important;
      gap: 8px !important;

      // 使用view模拟按钮，避开uni-button默认样式
      .dropdown-btn {
        width: 100% !important;
        padding: 6px 12px !important;
        border-radius: 6px !important;
        font-size: 14px !important;
        background: rgba(255, 255, 255, 0.1) !important;
        color: #fff !important;
        border: none !important;
        cursor: pointer !important;
        text-align: center !important;
        box-sizing: border-box !important;
        display: block !important;
        line-height: 1.4 !important;

        &:hover {
          background: rgba(255, 255, 255, 0.15) !important;
        }

        &.danger {
          background: rgba(220, 53, 69, 0.1) !important;
          color: #dc3545 !important;

          &:hover {
            background: rgba(220, 53, 69, 0.2) !important;
          }
        }
      }
    }
  }

}

// 全局样式：确保所有select下拉选项都使用暗色主题
select {
  option {
    background-color: #1a1a1a !important;
    color: #ffffff !important;
  }
}

// 针对WebKit浏览器的特殊处理
select::-webkit-scrollbar {
  width: 8px;
}

select::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
}

select::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
}

select::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}
</style>