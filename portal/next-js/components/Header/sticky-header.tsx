import Image from 'next/image';
import Link from 'next/link';

const StickyHeader = () => {
  return (
    <div className="logo-section">
      <table className="logo">
        <thead>
          <tr>
            <td className="logo">
              <Image
                width={100}
                height={100}
                src="/img/uno-icon-color.png"
                alt="University of Nebraska at Omaha Logo"
                className="uno-logo"
              />
            </td>
            <td className="right-end">
              <Link className="logo-text" href="/">
                Computer Science Learning Center
              </Link>
            </td>
          </tr>
        </thead>
      </table>
    </div>
  );
};

export default StickyHeader;
