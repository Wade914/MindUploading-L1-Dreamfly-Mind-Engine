// 思想元胞组件 - 用于展示和管理用户的思想内容
class ThoughtCell {
    constructor() {
        this.thoughtCellsContainer = null;
        this.currentUser = null;
        this.thoughtCells = [];
    }

    // 初始化组件
    init(containerId) {
        this.thoughtCellsContainer = document.getElementById(containerId);
        if (!this.thoughtCellsContainer) return;

        this.checkUserStatus();
        this.fetchThoughtCells();
    }

    // 检查用户状态
    checkUserStatus() {
        const storedUser = localStorage.getItem('currentUser');
        if (storedUser) {
            this.currentUser = JSON.parse(storedUser);
        }
    }

    // 获取思想元胞数据
    fetchThoughtCells() {
        // 在实际项目中，这里应该从API获取数据
        // 这里使用模拟数据
        this.thoughtCells = this.getMockThoughtCells();
        this.renderThoughtCells();
    }

    // 渲染思想元胞列表
    renderThoughtCells() {
        if (!this.thoughtCellsContainer || this.thoughtCells.length === 0) return;

        this.thoughtCellsContainer.innerHTML = '';

        this.thoughtCells.forEach(cell => {
            const cellElement = this.createThoughtCellElement(cell);
            this.thoughtCellsContainer.appendChild(cellElement);
        });
    }

    // 创建单个思想元胞元素
    createThoughtCellElement(cell) {
        const cellDiv = document.createElement('div');
        cellDiv.className = 'bg-white rounded-xl shadow-sm border border-gray-100 mb-6 overflow-hidden transition-custom hover:shadow-md';
        cellDiv.setAttribute('data-thought-id', cell.id);

        // 思想元胞HTML结构
        cellDiv.innerHTML = `
            <!-- 用户信息 -->
            <div class="p-4 flex items-start space-x-3">
                <div class="flex-shrink-0">
                    <a href="profile.html?id=${cell.userId}">
                        <img src="${cell.userAvatar}" alt="${cell.userName}" class="w-12 h-12 rounded-full object-cover border-2 border-gray-200">
                    </a>
                </div>
                <div class="flex-grow min-w-0">
                    <div class="flex items-center justify-between mb-1">
                        <div>
                            <h4 class="text-gray-900 font-semibold text-sm">
                                <a href="profile.html?id=${cell.userId}" class="hover:text-primary">${cell.userName}</a>
                            </h4>
                            <p class="text-gray-500 text-xs">${cell.timeAgo}</p>
                        </div>
                        <button class="text-gray-400 hover:text-gray-600 focus:outline-none" aria-label="更多选项">
                            <i class="fa fa-ellipsis-h"></i>
                        </button>
                    </div>
                    
                    <!-- 思想内容 -->
                    <div class="mb-3">
                        <p class="text-gray-800 text-sm whitespace-pre-line">${cell.content}</p>
                    </div>

                    <!-- 媒体内容（如果有） -->
                    ${cell.mediaUrl ? `
                    <div class="rounded-lg overflow-hidden mb-3">
                        <img src="${cell.mediaUrl}" alt="媒体内容" class="w-full h-auto object-cover">
                    </div>
                    ` : ''}

                    <!-- 标签（如果有） -->
                    ${cell.tags && cell.tags.length > 0 ? `
                    <div class="flex flex-wrap gap-2 mb-3">
                        ${cell.tags.map(tag => `
                            <a href="#" class="bg-gray-100 text-gray-700 text-xs px-3 py-1 rounded-full hover:bg-gray-200 transition-custom">
                                #${tag}
                            </a>
                        `).join('')}
                    </div>
                    ` : ''}

                    <!-- 交互统计 -->
                    <div class="flex items-center text-gray-500 text-xs border-t border-gray-100 pt-3 space-x-6">
                        <button class="flex items-center space-x-1 hover:text-primary transition-custom like-btn" data-thought-id="${cell.id}">
                            <i class="fa ${cell.isLiked ? 'fa-heart text-red-500' : 'fa-heart-o'}"></i>
                            <span>${cell.likesCount}</span>
                        </button>
                        <button class="flex items-center space-x-1 hover:text-primary transition-custom comment-btn" data-thought-id="${cell.id}">
                            <i class="fa fa-comment-o"></i>
                            <span>${cell.commentsCount}</span>
                        </button>
                        <button class="flex items-center space-x-1 hover:text-primary transition-custom share-btn" data-thought-id="${cell.id}">
                            <i class="fa fa-share"></i>
                            <span>${cell.sharesCount}</span>
                        </button>
                        <button class="flex items-center space-x-1 hover:text-primary transition-custom save-btn" data-thought-id="${cell.id}">
                            <i class="fa ${cell.isSaved ? 'fa-bookmark' : 'fa-bookmark-o'}"></i>
                            <span>${cell.isSaved ? '已收藏' : '收藏'}</span>
                        </button>
                    </div>
                </div>
            </div>
        `;

        // 添加事件监听器
        this.addEventListenersToCell(cellDiv, cell);

        return cellDiv;
    }

    // 为单个思想元胞添加事件监听器
    addEventListenersToCell(cellElement, cell) {
        // 点赞按钮
        const likeBtn = cellElement.querySelector('.like-btn');
        if (likeBtn) {
            likeBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleLike(cell.id);
            });
        }

        // 评论按钮
        const commentBtn = cellElement.querySelector('.comment-btn');
        if (commentBtn) {
            commentBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.showComments(cell.id);
            });
        }

        // 分享按钮
        const shareBtn = cellElement.querySelector('.share-btn');
        if (shareBtn) {
            shareBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.shareThoughtCell(cell.id);
            });
        }

        // 收藏按钮
        const saveBtn = cellElement.querySelector('.save-btn');
        if (saveBtn) {
            saveBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleSave(cell.id);
            });
        }
    }

    // 切换点赞状态
    toggleLike(thoughtId) {
        const thought = this.thoughtCells.find(cell => cell.id === thoughtId);
        if (!thought) return;

        if (thought.isLiked) {
            thought.likesCount--;
            thought.isLiked = false;
        } else {
            thought.likesCount++;
            thought.isLiked = true;
        }

        // 更新UI
        this.updateThoughtCellUI(thoughtId);
    }

    // 切换收藏状态
    async toggleSave(thoughtId) {
        const thought = this.thoughtCells.find(cell => cell.id === thoughtId);
        if (!thought) return;

        try {
            // 调用后端API
            const response = await toggleBookmark(thoughtId);

            if (response.success) {
                // 更新本地状态
                thought.isSaved = response.data.is_bookmarked;

                // 更新UI
                this.updateThoughtCellUI(thoughtId);

                // 显示提示消息
                console.log(response.data.message);
            } else {
                console.error('收藏操作失败:', response.msg);
                alert(response.msg || '收藏操作失败');
            }
        } catch (error) {
            console.error('收藏操作异常:', error);
            alert('收藏操作失败，请稍后重试');
        }
    }

    // 更新思想元胞UI
    updateThoughtCellUI(thoughtId) {
        const cellElement = document.querySelector(`[data-thought-id="${thoughtId}"]`);
        if (!cellElement) return;

        const thought = this.thoughtCells.find(cell => cell.id === thoughtId);
        if (!thought) return;

        // 更新点赞按钮
        const likeBtn = cellElement.querySelector('.like-btn');
        if (likeBtn) {
            const likeIcon = likeBtn.querySelector('i');
            const likeCount = likeBtn.querySelector('span');
            
            if (thought.isLiked) {
                likeIcon.className = 'fa fa-heart text-red-500';
            } else {
                likeIcon.className = 'fa fa-heart-o';
            }
            likeCount.textContent = thought.likesCount;
        }

        // 更新收藏按钮
        const saveBtn = cellElement.querySelector('.save-btn');
        if (saveBtn) {
            const saveIcon = saveBtn.querySelector('i');
            const saveText = saveBtn.querySelector('span');
            
            if (thought.isSaved) {
                saveIcon.className = 'fa fa-bookmark';
                saveText.textContent = '已收藏';
            } else {
                saveIcon.className = 'fa fa-bookmark-o';
                saveText.textContent = '收藏';
            }
        }
    }

    // 显示评论
    showComments(thoughtId) {
        // 实际项目中应该加载并显示评论
        alert(`显示思想元胞 ${thoughtId} 的评论`);
    }

    // 分享思想元胞
    shareThoughtCell(thoughtId) {
        // 实际项目中应该提供分享选项
        alert(`分享思想元胞 ${thoughtId}`);
    }

    // 添加新的思想元胞
    addThoughtCell(content, mediaUrl = null, tags = []) {
        if (!this.currentUser) {
            alert('请先登录');
            return;
        }

        const newCell = {
            id: Date.now().toString(),
            userId: this.currentUser.id,
            userName: this.currentUser.name,
            userAvatar: this.currentUser.avatar || 'https://picsum.photos/seed/user123/200/200',
            content: content,
            mediaUrl: mediaUrl,
            tags: tags,
            likesCount: 0,
            commentsCount: 0,
            sharesCount: 0,
            isLiked: false,
            isSaved: false,
            timeAgo: '刚刚'
        };

        this.thoughtCells.unshift(newCell);
        this.renderThoughtCells();

        // 实际项目中应该发送到服务器
        console.log('发布新的思想元胞:', newCell);
    }

    // 获取模拟数据
    getMockThoughtCells() {
        return [
            {
                id: '1',
                userId: '101',
                userName: '史蒂夫·乔布斯',
                userAvatar: 'https://picsum.photos/seed/jobs/200/200',
                content: 'Stay hungry, stay foolish. 求知若渴，虚怀若愚。这是我最喜欢的一句话，也是我想留给年轻一代的建议。不要满足于现状，永远保持对世界的好奇心和探索精神。',
                mediaUrl: 'https://picsum.photos/seed/apple/800/400',
                tags: ['人生感悟', '创新'],
                likesCount: 1243,
                commentsCount: 87,
                sharesCount: 56,
                isLiked: true,
                isSaved: false,
                timeAgo: '2小时前'
            },
            {
                id: '2',
                userId: '102',
                userName: '路德维希·维特根斯坦',
                userAvatar: 'https://picsum.photos/seed/wittgenstein/200/200',
                content: '凡是能够说的，都能够说清楚；凡是不能说的，就应该保持沉默。语言的边界就是思想的边界，我们的思考受到语言结构的限制。',
                tags: ['哲学', '语言'],
                likesCount: 567,
                commentsCount: 123,
                sharesCount: 34,
                isLiked: false,
                isSaved: true,
                timeAgo: '昨天'
            },
            {
                id: '3',
                userId: '103',
                userName: '阿尔伯特·爱因斯坦',
                userAvatar: 'https://picsum.photos/seed/einstein/200/200',
                content: '想象力比知识更重要。知识是有限的，而想象力概括着世界上的一切，推动着进步，并且是知识进化的源泉。',
                mediaUrl: 'https://picsum.photos/seed/physics/800/400',
                tags: ['科学', '创造力'],
                likesCount: 987,
                commentsCount: 65,
                sharesCount: 43,
                isLiked: false,
                isSaved: false,
                timeAgo: '3天前'
            }
        ];
    }
}

// 导出组件
if (typeof module !== 'undefined') {
    module.exports = ThoughtCell;
} else {
    // 浏览器环境下挂载到全局
    window.ThoughtCell = ThoughtCell;
}