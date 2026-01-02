'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { videoApi, scriptApi, postApi, uploadJobApi } from '@/lib/api';

export default function Dashboard() {
  const [stats, setStats] = useState({
    videos: 0,
    scripts: 0,
    posts: 0,
    pendingJobs: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const [videosRes, scriptsRes, postsRes, pendingJobsRes] = await Promise.all([
        videoApi.list(),
        scriptApi.list(),
        postApi.list(),
        uploadJobApi.getPending(),
      ]);

      setStats({
        videos: videosRes.data.total,
        scripts: scriptsRes.data.total,
        posts: postsRes.data.total,
        pendingJobs: pendingJobsRes.data.length,
      });
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const statsCards = [
    {
      title: '전체 영상',
      value: stats.videos,
      link: '/videos',
      color: 'bg-blue-500',
    },
    {
      title: '스크립트',
      value: stats.scripts,
      link: '/scripts',
      color: 'bg-green-500',
    },
    {
      title: 'AI 포스트',
      value: stats.posts,
      link: '/posts',
      color: 'bg-purple-500',
    },
    {
      title: '대기 중인 작업',
      value: stats.pendingJobs,
      link: '/upload-jobs',
      color: 'bg-orange-500',
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">로딩 중...</div>
      </div>
    );
  }

  return (
    <div className="px-4 sm:px-0">
      <div className="sm:flex sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">대시보드</h1>
          <p className="mt-2 text-sm text-gray-700">
            YouTube & Instagram 영상 자동 업로드 시스템
          </p>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="mt-8 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {statsCards.map((stat) => (
          <Link
            key={stat.title}
            href={stat.link}
            className="overflow-hidden rounded-lg bg-white shadow hover:shadow-lg transition-shadow"
          >
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className={`${stat.color} rounded-md p-3`}>
                    <div className="h-6 w-6 text-white font-bold flex items-center justify-center">
                      {stat.value}
                    </div>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="truncate text-sm font-medium text-gray-500">
                      {stat.title}
                    </dt>
                    <dd className="text-3xl font-semibold text-gray-900">
                      {stat.value}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="mt-8">
        <h2 className="text-lg font-medium text-gray-900 mb-4">빠른 작업</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <Link
            href="/videos/upload"
            className="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm hover:border-gray-400 hover:shadow-md transition"
          >
            <h3 className="text-lg font-medium text-gray-900">영상 업로드</h3>
            <p className="mt-2 text-sm text-gray-500">
              새 영상을 업로드하고 관리하세요
            </p>
          </Link>
          <Link
            href="/scripts/create"
            className="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm hover:border-gray-400 hover:shadow-md transition"
          >
            <h3 className="text-lg font-medium text-gray-900">스크립트 작성</h3>
            <p className="mt-2 text-sm text-gray-500">
              영상 대본을 작성하세요
            </p>
          </Link>
          <Link
            href="/posts/generate"
            className="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm hover:border-gray-400 hover:shadow-md transition"
          >
            <h3 className="text-lg font-medium text-gray-900">AI 포스트 생성</h3>
            <p className="mt-2 text-sm text-gray-500">
              GPT로 자동으로 바디글을 생성하세요
            </p>
          </Link>
        </div>
      </div>
    </div>
  );
}
