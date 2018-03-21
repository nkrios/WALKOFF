export class CacheConfig {

    static getDefault(): CacheConfig {
		return {
			type: 'disk',
            directory: './data/cache',
            shards: 1,
            timeout: 10,
            retry: true,
            host: 'localhost',
            port: 6379,
            unix_socket_path: ''
		};
	}

    type: string = 'disk';
	directory: string;
	shards: number;
	timeout: number;
	retry: boolean;
	host: string;
	port: number;
	unix_socket_path: string;
}
