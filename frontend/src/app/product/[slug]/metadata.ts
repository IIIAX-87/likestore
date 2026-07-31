import { Metadata } from 'next';
import { productsAPI } from '@/lib/api';

interface ProductPageProps {
  params: Promise<{ slug: string }>;
}

export async function generateMetadata({ params }: ProductPageProps): Promise<Metadata> {
  const resolvedParams = await params;
  const slug = resolvedParams.slug;

  try {
    const product = await productsAPI.detail(slug);

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const productAny = product as any;
    const title = productAny.meta_title || product.name;
    const description = productAny.meta_description || product.short_description || `${product.name} - купить в LikeStore. Гарантия 1 год.`;
    const image = product.main_image || undefined;
    const productUrl = `https://likestore.ru/product/${slug}/`;

    return {
      title,
      description,
      openGraph: {
        title,
        description,
        type: 'website' as const,
        url: productUrl,
        siteName: 'LikeStore',
        images: image ? [{ url: image, alt: product.name }] : [],
      },
      twitter: {
        card: 'summary_large_image' as const,
        title,
        description,
        images: image ? [image] : [],
      },
      alternates: {
        canonical: productUrl,
      },
    };
  } catch {
    return {
      title: 'Товар не найден | LikeStore',
      description: 'Запрошенный товар не найден',
    };
  }
}
