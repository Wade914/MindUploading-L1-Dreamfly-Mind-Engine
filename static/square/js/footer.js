// 页脚组件
class Footer {
    constructor() {
        this.footerElement = null;
    }

    // 初始化页脚
    init() {
        this.render();
        this.addEventListeners();
    }

    // 渲染页脚
    render() {
        const footerContainer = document.getElementById('footer-container');
        if (!footerContainer) return;

        const footerHTML = `
            <footer class="bg-gray-900 text-white py-12">
                <div class="container mx-auto px-4">
                    <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
                        <!-- 品牌信息 -->
                        <div>
                            <h3 class="text-2xl font-bold mb-4">
                                云己
                                <span class="text-primary-light">UpMe</span>
                            </h3>
                            <p class="text-gray-400 mb-6">
                                探索数字永生的无限可能，让思想超越时间与空间的界限。
                            </p>
                            <div class="flex space-x-4">
                                <a href="#" class="text-gray-400 hover:text-white transition-custom">
                                    <i class="fa fa-weibo text-xl"></i>
                                </a>
                                <a href="#" class="text-gray-400 hover:text-white transition-custom">
                                    <i class="fa fa-wechat text-xl"></i>
                                </a>
                                <a href="#" class="text-gray-400 hover:text-white transition-custom">
                                    <i class="fa fa-github text-xl"></i>
                                </a>
                                <a href="#" class="text-gray-400 hover:text-white transition-custom">
                                    <i class="fa fa-twitter text-xl"></i>
                                </a>
                            </div>
                        </div>

                        <!-- 功能导航 -->
                        <div>
                            <h4 class="text-lg font-semibold mb-4">核心功能</h4>
                            <ul class="space-y-2">
                                <li><a href="#" class="text-gray-400 hover:text-white transition-custom">梦蝶心智引擎</a></li>
                                <li><a href="#" class="text-gray-400 hover:text-white transition-custom">个人主页</a></li>
                                <li><a href="#" class="text-gray-400 hover:text-white transition-custom">思想元胞</a></li>
                                <li><a href="#" class="text-gray-400 hover:text-white transition-custom">生命数据库</a></li>
                                <li><a href="#" class="text-gray-400 hover:text-white transition-custom">星火墙</a></li>
                            </ul>
                        </div>

                        <!-- 资源中心 -->
                        <div>
                            <h4 class="text-lg font-semibold mb-4">资源中心</h4>
                            <ul class="space-y-2">
                                <li><a href="#" class="text-gray-400 hover:text-white transition-custom">开发文档</a></li>
                                <li><a href="#" class="text-gray-400 hover:text-white transition-custom">API参考</a></li>
                                <li><a href="#" class="text-gray-400 hover:text-white transition-custom">案例研究</a></li>
                                <li><a href="#" class="text-gray-400 hover:text-white transition-custom">研究论文</a></li>
                                <li><a href="#" class="text-gray-400 hover:text-white transition-custom">社区论坛</a></li>
                            </ul>
                        </div>

                        <!-- 关于我们 -->
                        <div>
                            <h4 class="text-lg font-semibold mb-4">关于我们</h4>
                            <ul class="space-y-2">
                                <li><a href="#" class="text-gray-400 hover:text-white transition-custom">项目愿景</a></li>
                                <li><a href="#" class="text-gray-400 hover:text-white transition-custom">开发团队</a></li>
                                <li><a href="#" class="text-gray-400 hover:text-white transition-custom">合作伙伴</a></li>
                                <li><a href="#" class="text-gray-400 hover:text-white transition-custom">联系方式</a></li>
                                <li><a href="#" class="text-gray-400 hover:text-white transition-custom">加入我们</a></li>
                            </ul>
                        </div>
                    </div>

                    <!-- 分隔线 -->
                    <div class="border-t border-gray-800 my-8"></div>

                    <!-- 底部信息 -->
                    <div class="flex flex-col md:flex-row justify-between items-center">
                        <div class="text-gray-500 text-sm mb-4 md:mb-0">
                            &copy; ${new Date().getFullYear()} 云己科技 UpMe Technology. 保留所有权利.
                        </div>
                        <div class="flex space-x-6">
                            <a href="#" class="text-gray-500 hover:text-gray-300 text-sm transition-custom">隐私政策</a>
                            <a href="#" class="text-gray-500 hover:text-gray-300 text-sm transition-custom">服务条款</a>
                            <a href="#" class="text-gray-500 hover:text-gray-300 text-sm transition-custom">法律声明</a>
                        </div>
                    </div>
                </div>
            </footer>
        `;

        footerContainer.innerHTML = footerHTML;
        this.footerElement = footerContainer.querySelector('footer');
    }

    // 添加事件监听器
    addEventListeners() {
        // 为所有链接添加点击事件处理
        const footerLinks = this.footerElement.querySelectorAll('a');
        footerLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                // 阻止默认行为，实际项目中可以根据需要处理
                e.preventDefault();
                
                // 获取链接文本或href用于进一步处理
                const linkText = link.textContent.trim();
                const linkHref = link.getAttribute('href');
                
                // 这里可以添加自定义的链接处理逻辑
                console.log(`点击了页脚链接: ${linkText} (${linkHref})`);
            });
        });
    }

    // 更新版权年份
    updateCopyrightYear() {
        const copyrightElement = this.footerElement.querySelector('div.text-gray-500.text-sm');
        if (copyrightElement) {
            const currentYear = new Date().getFullYear();
            copyrightElement.textContent = `© ${currentYear} 云己科技 UpMe Technology. 保留所有权利.`;
        }
    }

    // 显示/隐藏特定区域（用于响应式优化）
    toggleSection(sectionId, isVisible) {
        const section = this.footerElement.querySelector(`#${sectionId}`);
        if (section) {
            section.style.display = isVisible ? 'block' : 'none';
        }
    }
}

// 导出组件
if (typeof module !== 'undefined') {
    module.exports = Footer;
} else {
    // 浏览器环境下挂载到全局
    window.Footer = Footer;
}