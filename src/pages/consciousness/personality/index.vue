<template>
  <view class="personality-module">
    <!-- 主界面 -->
    <view v-if="!showTTFD">
      <view class="module-header">
        <text class="title">意识特征分析</text>
        <view class="ttfd-score">
          <text class="score-value">{{ ttfdScore }}%</text>
          <text class="score-label">意识协合度</text>
        </view>
      </view>

      <view class="personality-container">
        <!-- TTFD入口 -->
        <view class="ttfd-section">
          <view class="section-header">
            <text class="section-title">TTFD 意识同步测试</text>
            <text class="section-desc">数字生命的图灵测试</text>
          </view>
          <view class="ttfd-card" @click="startTTFD">
            <view class="card-left">
              <text class="card-icon">🤖</text>
              <view class="card-info">
                <text class="card-title">开始TTFD测试</text>
                <text class="card-desc">通过10个深度问题，评估意识同步程度</text>
              </view>
            </view>
            <text class="start-icon">→</text>
          </view>

          <!-- 没有mind文件的提示 -->
          <view class="mind-tip" v-if="showCreateMindTip">
            <text class="tip-icon">⚠️</text>
            <text class="tip-text">未找到您的意识体文件，测试将使用默认模式</text>
            <button class="create-mind-btn" @click="goToCreateMind">创建个人意识体</button>
          </view>
        </view>

        <!-- 心理量表测评区 -->
        <view class="assessment-selector">
          <view class="section-header">
            <text class="section-title">心理量表测评</text>
            <text class="section-desc">选择合适的量表开始测评</text>
          </view>
          <view class="assessment-grid">
            <view 
              v-for="(test, index) in psychometricTests" 
              :key="index"
              class="test-card"
              :class="{ 'completed': test.completed, 'active': currentTestIndex === index }"
              @click="selectTest(index)"
            >
              <text class="test-icon">{{ test.icon }}</text>
              <text class="test-name">{{ test.name }}</text>
              <text class="test-desc">{{ test.description }}</text>
              <text class="test-duration">预计用时: {{ test.duration }}</text>
              <view class="test-status" v-if="test.completed">
                <text class="status-icon">✓</text>
                <text class="status-text">已完成</text>
              </view>
            </view>
          </view>
        </view>

        <!-- 分析结果展示区 -->
        <view class="analysis-results" v-if="currentTestIndex !== null">
          <view class="section-header">
            <text class="section-title">{{ currentTestIndex === -1 ? 'TTFD测试结果' : '量表分析结果' }}</text>
            <text class="section-desc">{{ currentTestIndex === -1 ? '数字意识泛化能力评估' : '基于测评数据的性格特征分析' }}</text>
          </view>

          <!-- TTFD测试结果 -->
          <view class="ttfd-results" v-if="currentTestIndex === -1">
            <view class="consciousness-levels">
              <view 
                v-for="(level, index) in consciousnessLevels" 
                :key="index"
                class="level-card"
              >
                <view class="level-header">
                  <text class="level-name">L{{ level.level }}: {{ level.name }}</text>
                  <text class="level-score">{{ level.score }}%</text>
                </view>
                <view class="level-bar">
                  <view 
                    class="level-progress"
                    :style="{ width: level.score + '%' }"
                  ></view>
                </view>
                <text class="level-desc">{{ level.description }}</text>
                <view class="level-indicators">
                  <view 
                    v-for="(indicator, idx) in level.indicators"
                    :key="idx"
                    class="indicator-item"
                  >
                    <text class="indicator-name">{{ indicator.name }}</text>
                    <text class="indicator-value">{{ indicator.value }}</text>
                  </view>
                </view>
              </view>
            </view>
          </view>

          <!-- 量表分析结果 -->
          <view class="test-results" v-else>
            <view class="result-card">
              <view class="result-header">
                <text class="result-title">{{ psychometricTests[currentTestIndex].name }}分析报告</text>
                <text class="result-date">完成时间: {{ psychometricTests[currentTestIndex].completedDate }}</text>
              </view>
              <view class="result-content">
                <text class="result-text">{{ psychometricTests[currentTestIndex].analysis }}</text>
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- TTFD测试界面 -->
    <view v-else class="ttfd-test">
      <view class="test-header">
        <view class="header-left">
          <button class="back-btn" @click="closeTTFD">
            <text class="back-icon">←</text>
          </button>
          <text class="title">TTFD 意识同步测试</text>
        </view>
        <text class="progress">{{ currentQuestionIndex + 1 }} / {{ questions.length }}</text>
      </view>

      <view class="chat-container">
        <!-- 左侧：用户聊天窗口 -->
        <view class="chat-window user-window">
          <view class="window-header">
            <text class="window-title">本体对话</text>
          </view>
          <view class="chat-messages">
            <view 
              v-for="(message, index) in userMessages" 
              :key="'user-' + index"
              class="message"
              :class="{ 'question': message.type === 'question', 'answer': message.type === 'answer' }"
            >
              <text class="message-role" v-if="message.type === 'question'">评测师</text>
              <text class="message-role" v-if="message.type === 'answer'">本体</text>
              <text class="message-content">{{ message.content }}</text>
              <text class="message-time">{{ message.time }}</text>
            </view>
          </view>
          <view class="chat-input" v-if="!testCompleted">
            <textarea
              v-model="userInput"
              class="input-field"
              placeholder="输入你的回答..."
              :disabled="!canAnswer"
            />
            <button 
              class="send-btn"
              @click="submitUserAnswer"
              :disabled="!canAnswer || !userInput.trim()"
            >发送</button>
          </view>
        </view>

        <!-- 右侧：意识体聊天窗口 -->
        <view class="chat-window consciousness-window">
          <view class="window-header">
            <text class="window-title">意识体对话</text>
          </view>
          <view class="chat-messages">
            <view 
              v-for="(message, index) in consciousnessMessages" 
              :key="'consciousness-' + index"
              class="message"
              :class="{ 'question': message.type === 'question', 'answer': message.type === 'answer' }"
            >
              <text class="message-role" v-if="message.type === 'question'">评测师</text>
              <text class="message-role" v-if="message.type === 'answer'">意识体</text>
              <text class="message-content">{{ message.content }}</text>
              <text class="message-time">{{ message.time }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 测试完成提示 -->
      <view class="test-complete" v-if="testCompleted">
        <view class="complete-message">
          <text class="message-title">测试完成</text>
          <text class="message-desc">恭喜你完成了TTFD意识同步测试，现在可以生成详细的测评报告</text>
        </view>
        <view class="action-buttons">
          <button class="action-btn generate-btn" @click="generateReport">生成报告</button>
          <button class="action-btn close-btn" @click="closeTTFD">返回</button>
        </view>
      </view>
    </view>

    <!-- 测评弹窗 -->
    <view class="test-modal" v-if="showTestModal">
      <view class="modal-content">
        <view class="modal-header">
          <text class="modal-title">{{ currentTest.name }}</text>
          <button class="close-btn" @click="closeTest">×</button>
        </view>
        <view class="modal-body">
          <!-- 测试内容将根据不同量表动态渲染 -->
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { testAPI } from '@/utils/api.js'
import authManager from '@/utils/auth.js'

export default {
  name: 'PersonalityModule',
  data() {
    return {
      // API配置
      API_BASE_URL: 'http://localhost:8000',
      // 测试类型常量
      TEST_TYPE_TTFD: 'ttfd',
      showTTFD: false,
      loading: false,
      ttfdScore: 0,
      showTestModal: false,
      currentTest: null,
      currentTestIndex: null,
      ttfdCompleted: true,
      // 用户mind文件相关
      userMindData: null,
      userPersonalityPrompt: '',
      showCreateMindTip: false,
      // TTFD相关数据
      currentQuestionIndex: 0,
      userInput: '',
      userMessages: [],
      consciousnessMessages: [],
      canAnswer: true,
      testCompleted: false,
      questions: [
        "你喜欢什么颜色？",
        "你认为有外星人吗？",
        "你相信命运是由自己掌握的吗？",
        "当你在深夜独自思考时，最常浮现的念头是什么？",
        "如果必须选择，你会把最后一块面包留给哭泣的孩子，还是受伤的科学家？",
        "突然获得三天完全自由的时间，你第一件会做的事是什么？",
        '听到"玻璃碎裂声"时，你脑中首先浮现什么场景？',
        "当朋友的观点让你感到不适，你更可能当面质疑还是私下疏远？",
        "面对未完成的拼图，你倾向于通宵拼完还是改天继续？",
        "在陌生城市迷路时，你更相信手机导航还是直觉方向感？"
      ],
      // consciousnessAnswers 已删除硬编码回答，现在通过AI实时生成
      psychometricTests: [
        {
          icon: '🌳',
          name: '房树人测验',
          description: '通过绘画投射测试评估人格特征',
          duration: '20-30分钟',
          completed: false,
          completedDate: '',
          analysis: '通过绘画分析，您展现出较强的创造力和想象力。在人际交往中表现出开放和包容的态度，但有时会显得过于理想化。建议在决策时更多考虑现实因素。'
        },
        {
          icon: '📝',
          name: '普鲁斯特问卷',
          description: '探索个人偏好与价值观',
          duration: '15-20分钟',
          completed: false,
          completedDate: '',
          analysis: '您的价值观体系表现出对自由和创新的强烈追求。在生活态度上倾向于积极乐观，善于发现生活中的美好。对艺术和文学有较高的鉴赏力。'
        },
        {
          icon: '🎭',
          name: '大五人格测试',
          description: '评估核心人格维度',
          duration: '25-30分钟',
          completed: false,
          completedDate: '',
          analysis: '在开放性维度得分较高，表现出强烈的好奇心和求知欲。宜人性维度也较为突出，说明您善于理解和关心他人。情绪稳定性良好，能够有效应对压力。'
        },
        {
          icon: '🧩',
          name: '认知风格量表',
          description: '分析思维模式与决策倾向',
          duration: '20-25分钟',
          completed: false,
          completedDate: '',
          analysis: '您的思维模式偏向于整体性和系统性，善于发现事物之间的联系。在决策时倾向于收集充分信息后再做判断，但有时可能会显得犹豫不决。'
        }
      ],
      consciousnessLevels: [
        {
          level: 1,
          name: '表层反应层',
          score: 94,
          description: '直接的条件反射式回应能力',
          indicators: [
            { name: '反应速度', value: '极快' },
            { name: '匹配精度', value: '高' }
          ]
        },
        {
          level: 2,
          name: '经验关联层',
          score: 88,
          description: '基于个人经历的情境关联能力',
          indicators: [
            { name: '情境理解', value: '准确' },
            { name: '情绪共鸣', value: '良好' }
          ]
        },
        {
          level: 3,
          name: '价值推导层',
          score: 85,
          description: '价值体系和道德判断应用',
          indicators: [
            { name: '价值一致性', value: '稳定' },
            { name: '决策合理性', value: '较高' }
          ]
        },
        {
          level: 4,
          name: '认知模式层',
          score: 82,
          description: '思维习惯与问题解决策略',
          indicators: [
            { name: '逻辑连贯性', value: '优秀' },
            { name: '创新能力', value: '中等' }
          ]
        },
        {
          level: 5,
          name: '核心人格层',
          score: 79,
          description: '本质特性与深层动机',
          indicators: [
            { name: '人格稳定性', value: '高' },
            { name: '自我一致性', value: '良好' }
          ]
        }
      ]
    }
  },
  async mounted() {
    // 检查登录状态
    if (!authManager.isLoggedIn()) {
      authManager.requireLogin()
      return
    }

    await this.loadTestResults()
    await this.loadUserMind()
  },
  methods: {
    // 通用提示方法
    showToast(title, icon = 'none', duration = 2000) {
      uni.showToast({
        title,
        icon,
        duration
      });
    },

    // 调试日志方法
    debugLog(message, data = null) {
      if (process.env.NODE_ENV === 'development') {
        if (data) {
          console.log(message, data);
        } else {
          console.log(message);
        }
      }
    },

    // 通用错误处理方法
    handleError(error, message, showToast = false) {
      console.error(message, error);
      if (showToast) {
        this.showToast(message, 'error', 3000);
      }
    },

    // 加载用户的mind文件
    async loadUserMind() {
      try {
        const userInfo = authManager.getCurrentUser()
        if (!userInfo) {
          console.error('用户未登录')
          return
        }

        // 获取用户的mind文件列表
        const response = await uni.request({
          url: '/api/mind-list',
          method: 'GET'
        })

        // uni.request返回格式: [error, response]
        if (response[1] && response[1].data && response[1].data.code === 200) {
          const mindFiles = response[1].data.data

          // 查找用户的mind文件
          // 1. 优先查找用户名.mind
          // 2. 其次查找包含用户名的文件
          // 3. 最后查找包含邮箱前缀的文件
          let userMindFile = mindFiles.find(filename => filename === `${userInfo.username}.mind`)

          if (!userMindFile) {
            userMindFile = mindFiles.find(filename =>
              filename.includes(userInfo.username) ||
              filename.includes(userInfo.email.split('@')[0])
            )
          }

          if (userMindFile) {
            // 获取mind文件内容
            const mindResponse = await uni.request({
              url: `/api/mind/${userMindFile}`,
              method: 'GET'
            })

            if (mindResponse[1].data.code === 200) {
              const mindContent = mindResponse[1].data.data.content

              // 解析mind文件内容
              let mindData
              if (mindContent.includes('export default')) {
                const jsonStr = mindContent.replace(/export\s+default\s+/, '').trim()
                mindData = JSON.parse(jsonStr)
              } else {
                mindData = JSON.parse(mindContent)
              }

              // 保存用户的意识体数据
              this.userMindData = mindData

              // 构建完整的提示词，包含所有用户信息
              this.userPersonalityPrompt = this.buildCompletePrompt(mindData)

              this.debugLog('用户mind文件加载成功:', mindData.metadata.name)
            }
          } else {
            console.warn('未找到用户的mind文件')
            // 如果没有找到用户mind文件，提示用户创建
            this.showCreateMindTip = true
          }
        }
      } catch (error) {
        // 如果是网络错误或API不存在，静默处理
        if (error.message && error.message.includes('Cannot read properties of undefined')) {
          console.warn('Mind文件API不可用，将使用默认模式');
          this.showCreateMindTip = true;
        } else {
          this.handleError(error, '加载用户mind文件失败');
        }
      }
    },

    // 加载用户的测试结果
    async loadTestResults() {
      this.loading = true
      try {
        const testResults = await testAPI.getTestResults()

        // 查找TTFD测试结果
        const ttfdResult = testResults.find(result => result.test_type === this.TEST_TYPE_TTFD)
        if (ttfdResult) {
          this.ttfdScore = ttfdResult.score || 0
        }

        // 更新心理量表测试的完成状态
        testResults.forEach(result => {
          const test = this.psychometricTests.find(t => t.type === result.test_type)
          if (test) {
            test.completed = true
            test.score = result.score
          }
        })
      } catch (error) {
        console.error('加载测试结果失败:', error)
        // 不显示错误提示，保持默认状态
      } finally {
        this.loading = false
      }
    },
    selectTest(index) {
      this.currentTestIndex = index;
      if (index === -1) {
        // 跳转到TTFD测试页面
        this.startTTFD();
      } else {
        this.currentTest = this.psychometricTests[index];
        if (!this.currentTest.completed) {
          this.showTestModal = true;
        }
      }
    },
    startTest(test) {
      this.currentTest = test;
      this.showTestModal = true;
    },
    closeTest() {
      this.showTestModal = false;
      this.currentTest = null;
    },
    startTTFD() {
      this.showTTFD = true;
      this.askNextQuestion();
    },
    closeTTFD() {
      this.showTTFD = false;
      // 重置TTFD相关数据
      this.currentQuestionIndex = 0;
      this.userInput = '';
      this.userMessages = [];
      this.consciousnessMessages = [];
      this.canAnswer = true;
      this.testCompleted = false;
    },
    getCurrentTime() {
      const now = new Date();
      return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
    },
    askNextQuestion() {
      if (this.currentQuestionIndex < this.questions.length) {
        const question = this.questions[this.currentQuestionIndex];
        const time = this.getCurrentTime();

        // 向两个窗口添加问题
        this.userMessages.push({
          type: 'question',
          content: question,
          time
        });
        this.consciousnessMessages.push({
          type: 'question',
          content: question,
          time
        });

        // 现在只显示问题，等待用户回答
        // AI回答将在用户提交答案后生成
        this.canAnswer = true;
      } else {
        this.testCompleted = true;
      }
    },

    // 生成意识体回答
    async generateConsciousnessAnswer(question) {
      if (!this.userPersonalityPrompt) {
        this.showToast('请先创建个人意识体');
        return;
      }

      try {
        // 调用AI API生成回答 - 使用流式响应
        const response = await fetch(`${this.API_BASE_URL}/api/ai/chat/completions`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            messages: [
              { role: 'system', content: this.userPersonalityPrompt },
              { role: 'user', content: question }
            ],
            temperature: 0.7,
            max_tokens: 200,
            stream: true  // 改为流式响应
          })
        });

        if (!response.ok) {
          throw new Error(`AI API调用失败: ${response.status}`);
        }

        let aiAnswer = '';

        // 先添加一个空的回答消息，用于流式更新
        this.consciousnessMessages.push({
          type: 'answer',
          content: '',
          time: this.getCurrentTime()
        });

        // 处理流式响应
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.trim().startsWith('data: ')) {
              const jsonStr = line.trim().slice(6);
              if (jsonStr === '[DONE]') break;

              try {
                if (jsonStr) {
                  const data = JSON.parse(jsonStr);
                  const content = data.choices?.[0]?.delta?.content;
                  if (content) {
                    aiAnswer += content;
                    // 实时更新最后一条消息的内容
                    this.consciousnessMessages[this.consciousnessMessages.length - 1].content = aiAnswer;
                  }
                }
              } catch (e) {
                // 忽略解析错误，继续处理
                continue;
              }
            }
          }
        }

        // 如果没有生成内容，使用默认回答
        if (!aiAnswer.trim()) {
          aiAnswer = '我需要更多时间思考这个问题。';
          this.consciousnessMessages[this.consciousnessMessages.length - 1].content = aiAnswer;
        }

        this.debugLog(`问题: ${question}`);
        this.debugLog(`意识体回答: ${aiAnswer}`);
      } catch (error) {
        this.handleError(error, '生成意识体回答失败', true);
      }
    },
    async submitUserAnswer() {
      if (!this.userInput.trim()) return;

      // 添加用户回答
      this.userMessages.push({
        type: 'answer',
        content: this.userInput,
        time: this.getCurrentTime()
      });

      this.userInput = '';
      this.canAnswer = false;

      // 等待AI生成回答
      const currentQuestion = this.questions[this.currentQuestionIndex];
      await this.generateConsciousnessAnswer(currentQuestion);

      // AI回答完成后，再显示下一个问题
      this.currentQuestionIndex++;
      setTimeout(() => {
        this.askNextQuestion();
      }, 1000);
    },
    async generateReport() {
      try {
        // 计算TTFD得分
        const score = this.calculateTTFDScore();
        this.ttfdScore = score;

        // 准备测试结果数据
        const testData = {
          test_type: this.TEST_TYPE_TTFD,
          results: {
            score: score,
            questions_answered: this.questions.length,
            user_responses: this.userMessages.map(msg => msg.content),
            consciousness_levels: this.consciousnessLevels,
            completion_time: new Date().toISOString()
          },
          score: score,
          answers: {
            responses: this.userMessages.map((msg, index) => ({
              question_index: index,
              question: this.questions[index],
              answer: msg.content,
              timestamp: msg.time
            }))
          }
        };

        // 保存测试结果到后端
        await testAPI.saveTestResult(testData);

        // 更新意识层级数据
        this.updateConsciousnessLevels(score);

        // 关闭TTFD测试界面
        this.closeTTFD();

        // 显示TTFD测试结果
        this.currentTestIndex = -1;

        // 通知父组件更新意识协合度
        this.notifyParentRefresh();

        // 显示成功提示
        this.showToast('TTFD测试完成，意识协合度已更新', 'success', 3000);

      } catch (error) {
        console.error('保存TTFD测试结果失败:', error);

        // 即使保存失败，也显示本地结果
        const score = this.calculateTTFDScore();
        this.ttfdScore = score;
        this.updateConsciousnessLevels(score);
        this.closeTTFD();
        this.currentTestIndex = -1;

        this.showToast('报告生成成功，但保存失败', 'none', 3000);
      }
    },
    
    calculateTTFDScore() {
      // TTFD意识同步评分算法 - 基于余弦相似度计算
      let totalSimilarity = 0;
      let validAnswers = 0;

      // 获取用户的回答（过滤掉问题，只保留答案）
      const userAnswers = this.userMessages.filter(msg => msg.type === 'answer');
      // 获取意识体的回答（过滤掉问题，只保留答案）
      const consciousnessAnswers = this.consciousnessMessages.filter(msg => msg.type === 'answer');

      userAnswers.forEach((answer, index) => {
        if (index < consciousnessAnswers.length) {
          // 计算用户回答与意识体AI回答的余弦相似度
          const similarity = this.calculateCosineSimilarity(
            answer.content,
            consciousnessAnswers[index].content
          );
          totalSimilarity += similarity;
          validAnswers++;

          console.log(`问题${index + 1}:`);
          console.log(`  用户回答: ${answer.content}`);
          console.log(`  意识体回答: ${consciousnessAnswers[index].content}`);
          console.log(`  余弦相似度: ${(similarity * 100).toFixed(2)}%`);
        }
      });

      // 计算平均相似度
      const averageSimilarity = validAnswers > 0 ? totalSimilarity / validAnswers : 0;

      // 转换为TTFD得分 (50-98分区间)
      // 余弦相似度0-1映射到50-98分
      const finalScore = Math.round(averageSimilarity * 48 + 50);

      this.debugLog(`TTFD意识同步评分: 平均余弦相似度${(averageSimilarity * 100).toFixed(2)}%, 最终得分${finalScore}分`);

      return finalScore;
    },

    calculateCosineSimilarity(text1, text2) {
      // 1. 文本预处理和分词
      const words1 = this.tokenize(text1.toLowerCase());
      const words2 = this.tokenize(text2.toLowerCase());

      // 2. 创建词汇表（两个文本的所有唯一词汇）
      const vocabulary = [...new Set([...words1, ...words2])];

      if (vocabulary.length === 0) return 0;

      // 3. 向量化（计算词频向量）
      const vector1 = this.vectorize(words1, vocabulary);
      const vector2 = this.vectorize(words2, vocabulary);

      // 4. 计算余弦相似度
      return this.cosineDistance(vector1, vector2);
    },

    tokenize(text) {
      // 中文分词：结合字符分割和常见词汇分割
      const stopWords = ['的', '是', '在', '有', '和', '我', '你', '他', '她', '它', '了', '吗', '呢', '啊', '吧'];

      // 先按字符分割
      let tokens = text.split('');

      // 过滤停用词和标点符号
      tokens = tokens.filter(token =>
        token.trim() !== '' &&
        !stopWords.includes(token) &&
        !/[，。！？；：""''（）【】\s]/.test(token)
      );

      return tokens;
    },

    vectorize(words, vocabulary) {
      // 创建词频向量
      const vector = new Array(vocabulary.length).fill(0);

      words.forEach(word => {
        const index = vocabulary.indexOf(word);
        if (index !== -1) {
          vector[index]++;
        }
      });

      return vector;
    },

    cosineDistance(vector1, vector2) {
      // 计算余弦相似度: cos(θ) = (A·B) / (||A|| * ||B||)

      // 计算点积 (A·B)
      let dotProduct = 0;
      for (let i = 0; i < vector1.length; i++) {
        dotProduct += vector1[i] * vector2[i];
      }

      // 计算向量的模长 ||A|| 和 ||B||
      let magnitude1 = 0;
      let magnitude2 = 0;

      for (let i = 0; i < vector1.length; i++) {
        magnitude1 += vector1[i] * vector1[i];
        magnitude2 += vector2[i] * vector2[i];
      }

      magnitude1 = Math.sqrt(magnitude1);
      magnitude2 = Math.sqrt(magnitude2);

      // 避免除零错误
      if (magnitude1 === 0 || magnitude2 === 0) {
        return 0;
      }

      // 返回余弦相似度 (0-1之间)
      return dotProduct / (magnitude1 * magnitude2);
    },


    
    updateConsciousnessLevels(score) {
      // 根据总分更新各个层级的得分
      const baseScores = [94, 88, 85, 82, 79];
      const adjustment = (score - 87) / 10; // 基于原始87分的调整
      
      this.consciousnessLevels = this.consciousnessLevels.map((level, index) => ({
        ...level,
        score: Math.min(100, Math.max(0, baseScores[index] + adjustment * 5))
      }));
    },

    // 通知父组件刷新统计数据
    notifyParentRefresh() {
      // 使用事件总线通知父组件
      uni.$emit('refreshStats');

      // 也可以通过页面间通信
      const pages = getCurrentPages();
      if (pages.length > 1) {
        const prevPage = pages[pages.length - 2];
        if (prevPage && prevPage.refreshStats) {
          prevPage.refreshStats();
        }
      }
    },

    // 跳转到创建意识体页面
    goToCreateMind() {
      uni.navigateTo({
        url: '/pages/upload/minddata'
      });
    },

    // 构建完整的AI提示词
    buildCompletePrompt(mindData) {
      const metadata = mindData.metadata || {};
      const memory = mindData.memory || {};

      let prompt = `你现在是${metadata.name || '用户'}的数字意识体。`;

      // 添加基本信息
      if (metadata.birth) {
        const age = new Date().getFullYear() - new Date(metadata.birth).getFullYear();
        prompt += `你今年${age}岁，`;
      }

      if (metadata.occupation) {
        prompt += `职业是${metadata.occupation}。`;
      }

      // 添加自我认知
      if (memory.self_cognition) {
        prompt += `\n\n关于自我认知：${memory.self_cognition}`;
      }

      // 添加重要记忆片段
      if (memory.memory_fragments && memory.memory_fragments.length > 0) {
        prompt += `\n\n重要人生经历：`;
        memory.memory_fragments.forEach((fragment, index) => {
          if (fragment.time && fragment.content) {
            prompt += `\n${index + 1}. ${fragment.time}年：${fragment.content}`;
          }
        });
      }

      // 添加原始的人格描述
      if (metadata.personality_prompt && !metadata.personality_prompt.includes('你现在是')) {
        prompt += `\n\n人格特征：${metadata.personality_prompt}`;
      }

      // 添加行为指导
      prompt += `\n\n请基于以上信息，以${metadata.name || '用户'}的身份和思维方式回答问题。保持一致的人格特征、说话风格和价值观。`;

      this.debugLog('构建的完整提示词:', prompt);
      return prompt;
    }
  }
}
</script>

<style lang="scss">
// 定义全局变量
$primary-purple: rgba(171, 130, 255, 0.85);
$text-white: rgba(255, 255, 255, 0.9);
$text-gray: rgba(255, 255, 255, 0.6);

.personality-module {
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
    
    .ttfd-score {
      text-align: right;
      
      .score-value {
        font-size: 32px;
        font-weight: bold;
        color: #1890ff;
        display: block;
      }
      
      .score-label {
        font-size: 14px;
        color: rgba(255, 255, 255, 0.6);
      }
    }
  }
  
  .personality-container {
    display: grid;
    gap: 30px;
    
    .section-header {
      margin-bottom: 20px;
      
      .section-title {
        font-size: 18px;
        font-weight: 500;
        margin-bottom: 4px;
        display: block;
      }
      
      .section-desc {
        font-size: 14px;
        color: rgba(255, 255, 255, 0.6);
      }
    }
    
    .assessment-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
      gap: 20px;
      
      .test-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 20px;
        cursor: pointer;
        transition: all 0.3s;
        position: relative;
        
        &:hover {
          background: rgba(255, 255, 255, 0.08);
        }
        
        &.completed {
          border: 1px solid rgba(24, 144, 255, 0.3);
          
          .test-status {
            position: absolute;
            top: 12px;
            right: 12px;
            display: flex;
            align-items: center;
            gap: 4px;
            
            .status-icon {
              color: #1890ff;
            }
            
            .status-text {
              font-size: 12px;
              color: #1890ff;
            }
          }
        }
        
        &.active {
          border: 2px solid $primary-purple;
          box-shadow: 0 5px 25px rgba(171, 130, 255, 0.2);
        }
        
        &.ttfd-card {
          background: linear-gradient(135deg, rgba(171, 130, 255, 0.1), rgba(171, 130, 255, 0.05));
        }
        
        .test-icon {
          font-size: 24px;
          margin-bottom: 12px;
          display: block;
        }
        
        .test-name {
          font-size: 16px;
          font-weight: 500;
          margin-bottom: 8px;
          display: block;
        }
        
        .test-desc {
          font-size: 14px;
          color: rgba(255, 255, 255, 0.6);
          margin-bottom: 12px;
          line-height: 1.4;
        }
        
        .test-duration {
          font-size: 12px;
          color: rgba(255, 255, 255, 0.4);
        }
      }
    }
    
    .analysis-results {
      margin-top: 40px;
      padding: 20px;
      background: rgba(255, 255, 255, 0.05);
      border-radius: 16px;
      border: 1px solid rgba(255, 255, 255, 0.1);
      
      .result-card {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        padding: 20px;
        margin-top: 20px;
        
        .result-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
          
          .result-title {
            font-size: 18px;
            font-weight: 500;
            color: $primary-purple;
          }
          
          .result-date {
            font-size: 14px;
            color: $text-gray;
          }
        }
        
        .result-content {
          .result-text {
            font-size: 16px;
            line-height: 1.6;
            color: $text-white;
          }
        }
      }
    }
  }
  
  .test-modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    
    .modal-content {
      background: #1f1f1f;
      border-radius: 16px;
      width: 800px;
      max-height: 90vh;
      overflow-y: auto;
      
      .modal-header {
        padding: 20px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: sticky;
        top: 0;
        background: #1f1f1f;
        
        .modal-title {
          font-size: 20px;
          font-weight: 500;
        }
        
        .close-btn {
          background: transparent;
          border: none;
          color: rgba(255, 255, 255, 0.6);
          font-size: 24px;
          cursor: pointer;
          
          &:hover {
            color: #fff;
          }
        }
      }
      
      .modal-body {
        padding: 20px;
      }
    }
  }
}

.ttfd-section {
  margin-bottom: 40px;

  .ttfd-card {
    background: linear-gradient(135deg, rgba(171, 130, 255, 0.15), rgba(171, 130, 255, 0.05));
    border-radius: 16px;
    padding: 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    cursor: pointer;
    transition: all 0.3s ease;
    border: 1px solid rgba(171, 130, 255, 0.2);

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 5px 25px rgba(171, 130, 255, 0.2);
      border-color: rgba(171, 130, 255, 0.4);
    }

    .card-left {
      display: flex;
      align-items: center;
      gap: 20px;

      .card-icon {
        font-size: 32px;
      }

      .card-info {
        display: flex;
        flex-direction: column;
        gap: 4px;

        .card-title {
          font-size: 20px;
          font-weight: 500;
          color: $text-white;
        }

        .card-desc {
          font-size: 14px;
          color: $text-gray;
        }
      }
    }

    .start-icon {
      font-size: 24px;
      color: $primary-purple;
      transition: transform 0.3s ease;
    }

    &:hover .start-icon {
      transform: translateX(4px);
    }
  }

  .mind-tip {
    margin-top: 24px;
    padding: 24px;
    background: rgba(255, 193, 7, 0.1);
    border: 2px solid rgba(255, 193, 7, 0.3);
    border-radius: 16px;
    display: flex;
    flex-direction: column;
    align-items: center;

    .tip-icon {
      font-size: 32px;
      margin-bottom: 12px;
    }

    .tip-text {
      font-size: 14px;
      color: rgba(255, 255, 255, 0.8);
      text-align: center;
      margin-bottom: 16px;
      line-height: 1.4;
    }

    .create-mind-btn {
      padding: 12px 24px;
      background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%);
      border-radius: 20px;
      color: #000;
      font-size: 14px;
      font-weight: 500;
      border: none;
      cursor: pointer;
      transition: all 0.3s ease;

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(255, 193, 7, 0.3);
      }
    }
  }
}

.ttfd-test {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.95);
  z-index: 1000;
  padding: 20px;
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(10px);
  
  .test-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    margin-bottom: 20px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    
    .header-left {
      display: flex;
      align-items: center;
      gap: 20px;
      
      .back-btn {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: $text-gray;
        font-size: 24px;
        cursor: pointer;
        padding: 12px;
        border-radius: 50%;
        transition: all 0.3s ease;
        backdrop-filter: blur(5px);
        
        &:hover {
          background: rgba(255, 255, 255, 0.1);
          color: $text-white;
          transform: translateX(-4px);
        }
      }
      
      .title {
        font-size: 24px;
        font-weight: 500;
        color: $text-white;
        text-shadow: 0 0 20px rgba(171, 130, 255, 0.3);
        letter-spacing: 1px;
      }
    }
    
    .progress {
      font-size: 16px;
      color: $text-gray;
      padding: 8px 16px;
      background: rgba(255, 255, 255, 0.05);
      border-radius: 20px;
      border: 1px solid rgba(255, 255, 255, 0.1);
      backdrop-filter: blur(5px);
    }
  }
  
  .chat-container {
    display: flex;
    gap: 30px;
    flex: 1;
    min-height: 0;
    padding: 0 20px;
    
    .chat-window {
      flex: 1;
      display: flex;
      flex-direction: column;
      background: rgba(255, 255, 255, 0.05);
      border-radius: 16px;
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      overflow: hidden;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
      max-width: 50%;
      
      .window-header {
        padding: 16px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        background: rgba(255, 255, 255, 0.03);
        
        .window-title {
          font-size: 16px;
          font-weight: 500;
          color: $text-white;
          letter-spacing: 1px;
        }
      }
      
      .chat-messages {
        flex: 1;
        overflow-y: auto;
        padding: 16px;
        
        .message {
          margin-bottom: 16px;
          max-width: 85%;
          animation: fadeIn 0.3s ease;
          
          &.question {
            margin-left: auto;
            
            .message-role {
              text-align: right;
              margin-bottom: 4px;
              color: $primary-purple;
              font-size: 12px;
              text-shadow: 0 0 10px rgba(171, 130, 255, 0.3);
            }
            
            .message-content {
              background: rgba(171, 130, 255, 0.15);
              padding: 12px 16px;
              border-radius: 16px 16px 0 16px;
              color: $text-white;
              font-size: 14px;
              line-height: 1.5;
              border: 1px solid rgba(171, 130, 255, 0.2);
              backdrop-filter: blur(5px);
            }
            
            .message-time {
              text-align: right;
              margin-top: 4px;
              font-size: 11px;
              color: $text-gray;
            }
          }
          
          &.answer {
            margin-right: auto;
            
            .message-role {
              margin-bottom: 4px;
              color: $primary-purple;
              font-size: 12px;
              text-shadow: 0 0 10px rgba(171, 130, 255, 0.3);
            }
            
            .message-content {
              background: rgba(255, 255, 255, 0.05);
              padding: 12px 16px;
              border-radius: 16px 16px 16px 0;
              color: $text-white;
              font-size: 14px;
              line-height: 1.5;
              border: 1px solid rgba(255, 255, 255, 0.1);
              backdrop-filter: blur(5px);
            }
            
            .message-time {
              margin-top: 4px;
              font-size: 11px;
              color: $text-gray;
            }
          }
        }
      }
      
      .chat-input {
        padding: 16px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        gap: 12px;
        background: rgba(255, 255, 255, 0.03);
        
        .input-field {
          flex: 1;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 8px;
          padding: 12px;
          color: $text-white;
          font-size: 14px;
          resize: none;
          height: 80px;
          transition: all 0.3s ease;
          backdrop-filter: blur(5px);
          
          &:focus {
            outline: none;
            border-color: $primary-purple;
            background: rgba(255, 255, 255, 0.08);
            box-shadow: 0 0 15px rgba(171, 130, 255, 0.1);
          }
          
          &:disabled {
            opacity: 0.5;
            cursor: not-allowed;
          }
        }
        
        .send-btn {
          align-self: flex-end;
          background: $primary-purple;
          border: none;
          color: $text-white;
          padding: 12px 20px;
          border-radius: 8px;
          font-size: 14px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.3s ease;
          backdrop-filter: blur(5px);
          
          &:hover {
            transform: translateY(-1px);
            box-shadow: 0 3px 10px rgba(171, 130, 255, 0.2);
          }
          
          &:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
          }
        }
      }
    }
  }
  
  .test-complete {
    position: fixed;
    bottom: 40px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 20px;
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    animation: slideUp 0.5s ease;
    
    .complete-message {
      text-align: center;
      margin-bottom: 20px;
      
      .message-title {
        font-size: 20px;
        font-weight: 500;
        color: $text-white;
        margin-bottom: 8px;
      }
      
      .message-desc {
        font-size: 14px;
        color: $text-gray;
      }
    }
    
    .action-buttons {
      display: flex;
      gap: 16px;
      justify-content: center;
      
      .action-btn {
        padding: 12px 24px;
        border-radius: 12px;
        font-size: 16px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        backdrop-filter: blur(5px);
        
        &.generate-btn {
          background: $primary-purple;
          color: $text-white;
          border: none;
          
          &:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(171, 130, 255, 0.3);
          }
        }
        
        &.close-btn {
          background: rgba(255, 255, 255, 0.05);
          color: $text-white;
          border: 1px solid rgba(255, 255, 255, 0.1);
          
          &:hover {
            background: rgba(255, 255, 255, 0.1);
            transform: translateY(-2px);
          }
        }
      }
    }
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translate(-50%, 20px);
  }
  to {
    opacity: 1;
    transform: translate(-50%, 0);
  }
}
</style> 